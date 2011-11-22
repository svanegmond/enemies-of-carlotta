"""Mailing list manager.

This is a simple mailing list manager that mimicks the ezmlm-idx mail
address commands. See manual page for more information.
"""

VERSION = "1.2.6"
PLUGIN_INTERFACE_VERSION = "1"

import getopt
import md5
import os
import shutil
import smtplib
import string
import sys
import time
import ConfigParser
try:
    import email.Header
    have_email_module = 1
except ImportError:
    have_email_module = 0
import imp

import qmqp


# The following values will be overriden by "make install".
TEMPLATE_DIRS = ["./templates"]
DOTDIR = "dot-eoc"


class EocException(Exception):

    def __init__(self, arg=None):
        self.msg = repr(arg)

    def __str__(self):
        return self.msg

class UnknownList(EocException):
    def __init__(self, list_name):
        self.msg = "%s is not a known mailing list" % list_name

class BadCommandAddress(EocException):
    def __init__(self, address):
        self.msg = "%s is not a valid command address" % address

class BadSignature(EocException):
    def __init__(self, address):
        self.msg = "address %s has an invalid digital signature" % address

class ListExists(EocException):
    def __init__(self, list_name):
        self.msg = "Mailing list %s alreadys exists" % list_name

class ListDoesNotExist(EocException):
    def __init__(self, list_name):
        self.msg = "Mailing list %s does not exist" % list_name

class MissingEnvironmentVariable(EocException):
    def __init__(self, name):
        self.msg = "Environment variable %s does not exist" % name

class MissingTemplate(EocException):
    def __init__(self, template):
        self.msg = "Template %s does not exit" % template


# Names of commands EoC recognizes in e-mail addresses.
SIMPLE_COMMANDS = ["help", "list", "owner", "setlist", "setlistsilently", "ignore"]
SUB_COMMANDS = ["subscribe", "unsubscribe"]
HASH_COMMANDS = ["subyes", "subapprove", "subreject", "unsubyes",
                 "bounce", "probe", "approve", "reject", "setlistyes",
                 "setlistsilentyes"]
COMMANDS = SIMPLE_COMMANDS + SUB_COMMANDS + HASH_COMMANDS


def md5sum_as_hex(s):
    return md5.new(s).hexdigest()


def forkexec(argv, text):
    """Run a command (given as argv array) and write text to its stdin"""
    (r, w) = os.pipe()
    pid = os.fork()
    if pid == -1:
        raise Exception("fork failed")
    elif pid == 0:
        os.dup2(r, 0)
        os.close(r)
        os.close(w)
        fd = os.open("/dev/null", os.O_RDWR)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        os.execvp(argv[0], argv)
        sys.exit(1)
    else:
        os.close(r)
        os.write(w, text)
        os.close(w)
        (pid2, exit) = os.waitpid(pid, 0)
        if pid != pid2:
            raise Exception("os.waitpid for %d returned for %d" % (pid, pid2))
        if exit != 0:
            raise Exception("subprocess failed, exit=0x%x" % exit)
        return exit


environ = None

def set_environ(new_environ):
    global environ
    environ = new_environ

def get_from_environ(key):
    global environ
    if environ:
        env = environ
    else:
        env = os.environ
    if env.has_key(key):
        return env[key].lower()
    raise MissingEnvironmentVariable(key)

class AddressParser:

    """A parser for incoming e-mail addresses."""

    def __init__(self, lists):
        self.set_lists(lists)
        self.set_skip_prefix(None)
        self.set_forced_domain(None)

    def set_lists(self, lists):
        """Set the list of canonical list names we should know about."""
        self.lists = lists

    def set_skip_prefix(self, skip_prefix):
        """Set the prefix to be removed from an address."""
        self.skip_prefix = skip_prefix
        
    def set_forced_domain(self, forced_domain):
        """Set the domain part we should force the address to have."""
        self.forced_domain = forced_domain

    def clean(self, address):
        """Remove cruft from the address and convert the rest to lower case."""
        if self.skip_prefix:
            n = self.skip_prefix and len(self.skip_prefix)
            if address[:n] == self.skip_prefix:
                address = address[n:]
        if self.forced_domain:
            parts = address.split("@", 1)
            address = "%s@%s" % (parts[0], self.forced_domain)
        return address.lower()

    def split_address(self, address):
        """Split an address to a local part and a domain."""
        parts = address.lower().split("@", 1)
        if len(parts) != 2:
            return (address, "")
        else:
            return parts

    # Does an address refer to a list? If not, return None, else return a list
    # of additional parts (separated by hyphens) in the address. Note that []
    # is not the same as None.
    
    def additional_address_parts(self, address, listname):
        addr_local, addr_domain = self.split_address(address)
        list_local, list_domain = self.split_address(listname)
        
        if addr_domain != list_domain:
            return None
        
        if addr_local.lower() == list_local.lower():
            return []
        
        n = len(list_local)
        if addr_local[:n] != list_local or addr_local[n] != "-":
            return None
            
        return addr_local[n+1:].split("-")
        

    # Parse an address we have received that identifies a list we manage.
    # The address may contain command and signature parts. Return the name
    # of the list, and a sequence of the additional parts (split at hyphens).
    # Raise exceptions for errors. Note that the command will be valid, but
    # cryptographic signatures in the address is not checked.
    
    def parse(self, address):
        address = self.clean(address)
        for listname in self.lists:
            parts = self.additional_address_parts(address, listname)
            if parts == None:
                pass
            elif parts == []:
                return listname, parts
            elif parts[0] in HASH_COMMANDS:
                if len(parts) != 3:
                    raise BadCommandAddress(address)
                return listname, parts
            elif parts[0] in COMMANDS:
                return listname, parts

        raise UnknownList(address)


class MailingListManager:

    def __init__(self, dotdir, sendmail="/usr/sbin/sendmail", lists=[],
                 smtp_server=None, qmqp_server=None):
        self.dotdir = dotdir
        self.sendmail = sendmail
        self.smtp_server = smtp_server
        self.qmqp_server = qmqp_server

        self.make_dotdir()
        self.secret = self.make_and_read_secret()

        if not lists:
            lists = filter(lambda s: "@" in s, os.listdir(dotdir))
        self.set_lists(lists)

        self.simple_commands = ["help", "list", "owner", "setlist",
                                "setlistsilently", "ignore"]
        self.sub_commands = ["subscribe", "unsubscribe"]
        self.hash_commands = ["subyes", "subapprove", "subreject", "unsubyes",
                              "bounce", "probe", "approve", "reject",
                              "setlistyes", "setlistsilentyes"]
        self.commands = self.simple_commands + self.sub_commands + \
                        self.hash_commands

        self.environ = None

        self.load_plugins()
        
    # Create the dot directory for us, if it doesn't exist already.
    def make_dotdir(self):
        if not os.path.isdir(self.dotdir):
            os.makedirs(self.dotdir, 0700)

    # Create the "secret" file, with a random value used as cookie for
    # verification addresses.
    def make_and_read_secret(self):
        secret_name = os.path.join(self.dotdir, "secret")
        if not os.path.isfile(secret_name):
            f = open("/dev/urandom", "r")
            secret = f.read(32)
            f.close()
            f = open(secret_name, "w")
            f.write(secret)
            f.close()
        else:
            f = open(secret_name, "r")
            secret = f.read()
            f.close()
        return secret

    # Load the plugins from DOTDIR/plugins/*.py.
    def load_plugins(self):
        self.plugins = []

        dirname = os.path.join(DOTDIR, "plugins")
        try:
            plugins = os.listdir(dirname)
        except OSError:
            return
            
        plugins.sort()
        plugins = map(os.path.splitext, plugins)
        plugins = filter(lambda p: p[1] == ".py", plugins)
        plugins = map(lambda p: p[0], plugins)
        for name in plugins:
            pathname = os.path.join(dirname, name + ".py")
            f = open(pathname, "r")
            module = imp.load_module(name, f, pathname, 
                                     (".py", "r", imp.PY_SOURCE))
            f.close()
            if module.PLUGIN_INTERFACE_VERSION == PLUGIN_INTERFACE_VERSION:
                self.plugins.append(module)

    # Call function named funcname (a string) in all plugins, giving as
    # arguments all the remaining arguments preceded by ml. Return value
    # of each function is the new list of arguments to the next function.
    # Return value of this function is the return value of the last function.
    def call_plugins(self, funcname, list, *args):
        for plugin in self.plugins:
            if plugin.__dict__.has_key(funcname):
                args = apply(plugin.__dict__[funcname], (list,) + args)
                if type(args) != type((0,)):
                    args = (args,)
        return args

    # Set the list of listnames. The list of lists needs to be sorted in
    # length order so that test@example.com is matched before
    # test-list@example.com
    def set_lists(self, lists):
        temp = map(lambda s: (len(s), s), lists)
        temp.sort()
        self.lists = map(lambda t: t[1], temp)

    # Return the list of listnames.
    def get_lists(self):
        return self.lists

    # Decode an address that has been encoded to be part of a local part.
    def decode_address(self, parts):
        return string.join(string.join(parts, "-").split("="), "@")

    # Is local_part@domain an existing list?
    def is_list_name(self, local_part, domain):
        return ("%s@%s" % (local_part, domain)) in self.lists

    # Compute the verification checksum for an address.
    def compute_hash(self, address):
        return md5sum_as_hex(address + self.secret)

    # Is the verification signature in a parsed address bad? If so, return true,
    # otherwise return false.
    def signature_is_bad(self, dict, hash):
        local_part, domain = dict["name"].split("@")
        address = "%s-%s-%s@%s" % (local_part, dict["command"], dict["id"], 
                                   domain)
        correct = self.compute_hash(address)
        return correct != hash

    # Parse a command address we have received and check its validity
    # (including signature, if any). Return a dictionary with keys
    # "command", "sender" (address that was encoded into address, if
    # any), "id" (group ID).

    def parse_recipient_address(self, address, skip_prefix, forced_domain):
        ap = AddressParser(self.get_lists())
        ap.set_lists(self.get_lists())
        ap.set_skip_prefix(skip_prefix)
        ap.set_forced_domain(forced_domain)
        listname, parts = ap.parse(address)

        dict = { "name": listname }

        if parts == []:
            dict["command"] = "post"
        else:
            command, args = parts[0], parts[1:]
            dict["command"] = command
            if command in SUB_COMMANDS:
                dict["sender"] = self.decode_address(args)
            elif command in HASH_COMMANDS:
                dict["id"] = args[0]
                hash = args[1]
                if self.signature_is_bad(dict, hash):
                    raise BadSignature(address)

        return dict

    # Does an address refer to a mailing list?
    def is_list(self, name, skip_prefix=None, domain=None):
        try:
            self.parse_recipient_address(name, skip_prefix, domain)
        except BadCommandAddress:
            return 0
        except BadSignature:
            return 0
        except UnknownList:
            return 0
        return 1

    # Create a new list and return it.
    def create_list(self, name):
        if self.is_list(name):
            raise ListExists(name)
        self.set_lists(self.lists + [name])
        return MailingList(self, name)

    # Open an existing list.
    def open_list(self, name):
        if self.is_list(name):
            return self.open_list_exact(name)
        else:
            x = name + "@"
            for list in self.lists:
                if list[:len(x)] == x:
                    return self.open_list_exact(list)
            raise ListDoesNotExist(name)

    def open_list_exact(self, name):
        for list in self.get_lists():
            if list.lower() == name.lower():
                return MailingList(self, list)
        raise ListDoesNotExist(name)

    # Process an incoming message.
    def incoming_message(self, skip_prefix, domain, moderate, post):
        debug("Processing incoming message.")
        debug("$SENDER = <%s>" % get_from_environ("SENDER"))
        debug("$RECIPIENT = <%s>" % get_from_environ("RECIPIENT"))
        dict = self.parse_recipient_address(get_from_environ("RECIPIENT"),
                                                             skip_prefix, 
                                                             domain)
        dict["force-moderation"] = moderate
        dict["force-posting"] = post
        debug("List is <%(name)s>, command is <%(command)s>." % dict)
        list = self.open_list_exact(dict["name"])
        list.obey(dict)

    # Clean up bouncing address and do other janitorial work for all lists.
    def cleaning_woman(self, send_mail=None):
        now = time.time()
        for listname in self.lists:
            list = self.open_list_exact(listname)
            if send_mail:
                list.send_mail = send_mail
            list.cleaning_woman(now)

    # Send a mail to the desired recipients.
    def send_mail(self, envelope_sender, recipients, text):
        debug("send_mail:\n  sender=%s\n  recipients=%s\n  text=\n    %s" % 
              (envelope_sender, str(recipients), 
               "\n    ".join(text[:text.find("\n\n")].split("\n"))))
        if recipients:
            if self.smtp_server:
                try:
                    smtp = smtplib.SMTP(self.smtp_server)
                    smtp.sendmail(envelope_sender, recipients, text)
                    smtp.quit()
                except:
                    error("Error sending SMTP mail, mail probably not sent")
                    sys.exit(1)
            elif self.qmqp_server:
                try:
                    q = qmqp.QMQP(self.qmqp_server)
                    q.sendmail(envelope_sender, recipients, text)
                    q.quit()
                except:
                    error("Error sending QMQP mail, mail probably not sent")
                    sys.exit(1)
            else:
                status = forkexec([self.sendmail, "-oi", "-f", 
                                   envelope_sender] + recipients, text)
                if status:
                    error("%s returned %s, mail sending probably failed" %
                           (self.sendmail, status))
                    sys.exit((status >> 8) & 0xff)
        else:
            debug("send_mail: no recipients, not sending")



class MailingList:

    posting_opts = ["auto", "free", "moderated"]

    def __init__(self, mlm, name):
        self.mlm = mlm
        self.name = name

        self.cp = ConfigParser.ConfigParser()
        self.cp.add_section("list")
        self.cp.set("list", "owners", "")
        self.cp.set("list", "moderators", "")
        self.cp.set("list", "subscription", "free")
        self.cp.set("list", "posting", "free")
        self.cp.set("list", "archived", "no")
        self.cp.set("list", "mail-on-subscription-changes", "no")
        self.cp.set("list", "mail-on-forced-unsubscribe", "no")
        self.cp.set("list", "ignore-bounce", "no")
        self.cp.set("list", "language", "")
        self.cp.set("list", "pristine-headers", "")

        self.dirname = os.path.join(self.mlm.dotdir, name)
        self.make_listdir()
        self.cp.read(self.mkname("config"))

        self.subscribers = SubscriberDatabase(self.dirname, "subscribers")
        self.moderation_box = MessageBox(self.dirname, "moderation-box")
        self.subscription_box = MessageBox(self.dirname, "subscription-box")
        self.bounce_box = MessageBox(self.dirname, "bounce-box")

    def make_listdir(self):
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname, 0700)
            self.save_config()
            f = open(self.mkname("subscribers"), "w")
            f.close()

    def mkname(self, relative):
        return os.path.join(self.dirname, relative)

    def save_config(self):
        f = open(self.mkname("config"), "w")
        self.cp.write(f)
        f.close()

    def read_stdin(self):
        data = sys.stdin.read()
        # Convert CRLF to plain LF
        data = "\n".join(data.split("\r\n"))
        # Skip Unix mbox "From " mail start indicator
        if data[:5] == "From ":
            data = string.split(data, "\n", 1)[1]
        return data

    def invent_boundary(self):
        return "%s/%s" % (md5sum_as_hex(str(time.time())),
                          md5sum_as_hex(self.name))

    def command_address(self, command):
        local_part, domain = self.name.split("@")
        return "%s-%s@%s" % (local_part, command, domain)

    def signed_address(self, command, id):
        unsigned = self.command_address("%s-%s" % (command, id))
        hash = self.mlm.compute_hash(unsigned)
        return self.command_address("%s-%s-%s" % (command, id, hash))

    def ignore(self):
        return self.command_address("ignore")

    def nice_7bit(self, str):
        for c in str:
            if (ord(c) < 32 and not c.isspace()) or ord(c) >= 127:
                return False
        return True
    
    def mime_encode_headers(self, text):
        try:
            headers, body = text.split("\n\n", 1)
        
            list = []
            for line in headers.split("\n"):
                if line[0].isspace():
                    list[-1] += line
                else:
                    list.append(line)
        
            headers = []
            for header in list:
                if self.nice_7bit(header):
                    headers.append(header)
                else:
                    if ": " in header:
                        name, content = header.split(": ", 1)
                    else:
                        name, content = header.split(":", 1)
                    hdr = email.Header.Header(content, "utf-8")
                    headers.append(name + ": " + hdr.encode())
        
            return "\n".join(headers) + "\n\n" + body
        except:
            info("Cannot MIME encode header, using original ones, sorry")
            return text

    def template(self, template_name, dict):
        lang = self.cp.get("list", "language")
        if lang:
            template_name_lang = template_name + "." + lang
        else:
            template_name_lang = template_name

        if not dict.has_key("list"):
            dict["list"] = self.name
            dict["local"], dict["domain"] = self.name.split("@")
        if not dict.has_key("list"):
            dict["list"] = self.name

        for dir in [os.path.join(self.dirname, "templates")] + TEMPLATE_DIRS:
            pathname = os.path.join(dir, template_name_lang)
            if not os.path.exists(pathname):
                pathname = os.path.join(dir, template_name)
            if os.path.exists(pathname):
                f = open(pathname, "r")
                data = f.read()
                f.close()
                return data % dict

        raise MissingTemplate(template_name)

    def send_template(self, envelope_sender, sender, recipients,
                      template_name, dict):
        dict["From"] = "EoC <%s>" % sender
        dict["To"] = string.join(recipients, ", ")
        text = self.template(template_name, dict)
        if not text:
            return
        if self.cp.get("list", "pristine-headers") != "yes":
            text = self.mime_encode_headers(text)
        self.mlm.send_mail(envelope_sender, recipients, text)

    def send_info_message(self, recipients, template_name, dict):
        self.send_template(self.command_address("ignore"),
                           self.command_address("help"),
                           recipients,
                           template_name,
                           dict)

    def owners(self):
        return self.cp.get("list", "owners").split()

    def moderators(self):
        return self.cp.get("list", "moderators").split()

    def is_list_owner(self, address):
        return address in self.owners()

    def obey_help(self):
        self.send_info_message([get_from_environ("SENDER")], "help", {})

    def obey_list(self):
        recipient = get_from_environ("SENDER")
        if self.is_list_owner(recipient):
            addr_list = self.subscribers.get_all()
            addr_text = string.join(addr_list, "\n")
            self.send_info_message([recipient], "list",
                                   {
                                     "addresses": addr_text,
                                     "count": len(addr_list),
                                   })
        else:
            self.send_info_message([recipient], "list-sorry", {})

    def obey_setlist(self, origmail):
        recipient = get_from_environ("SENDER")
        if self.is_list_owner(recipient):
            id = self.moderation_box.add(recipient, origmail)
            if self.parse_setlist_addresses(origmail) == None:
                self.send_bad_addresses_in_setlist(id)
                self.moderation_box.remove(id)
            else:
                confirm = self.signed_address("setlistyes", id)
                self.send_info_message(self.owners(), "setlist-confirm",
                                       {
                                          "confirm": confirm,
                                          "origmail": origmail,
                                          "boundary": self.invent_boundary(),
                                       })
                
        else:
            self.send_info_message([recipient], "setlist-sorry", {})

    def obey_setlistsilently(self, origmail):
        recipient = get_from_environ("SENDER")
        if self.is_list_owner(recipient):
            id = self.moderation_box.add(recipient, origmail)
            if self.parse_setlist_addresses(origmail) == None:
                self.send_bad_addresses_in_setlist(id)
                self.moderation_box.remove(id)
            else:
                confirm = self.signed_address("setlistsilentyes", id)
                self.send_info_message(self.owners(), "setlist-confirm",
                                       {
                                          "confirm": confirm,
                                          "origmail": origmail,
                                          "boundary": self.invent_boundary(),
                                       })
        else:
            self.send_info_message([recipient], "setlist-sorry", {})

    def parse_setlist_addresses(self, text):
        body = text.split("\n\n", 1)[1]
        lines = body.split("\n")
        lines = filter(lambda line: line != "", lines)
        badlines = filter(lambda line: "@" not in line, lines)
        if badlines:
            return None
        else:
            return lines

    def send_bad_addresses_in_setlist(self, id):
        addr = self.moderation_box.get_address(id)
        origmail = self.moderation_box.get(id)
        self.send_info_message([addr], "setlist-badlist",
                               {
                                "origmail": origmail,
                                "boundary": self.invent_boundary(),
                               })


    def obey_setlistyes(self, dict):
        if self.moderation_box.has(dict["id"]):
            text = self.moderation_box.get(dict["id"])
            addresses = self.parse_setlist_addresses(text)
            if addresses == None:
                self.send_bad_addresses_in_setlist(id)
            else:
                removed_subscribers = []
                self.subscribers.lock()
                old = self.subscribers.get_all()
                for address in old:
                    if address.lower() not in map(string.lower, addresses):
                        self.subscribers.remove(address)
                        removed_subscribers.append(address)
                    else:
                        for x in addresses:
                            if x.lower() == address.lower():
                                addresses.remove(x)
                self.subscribers.add_many(addresses)
                self.subscribers.save()
                
                for recipient in addresses:
                    self.send_info_message([recipient], "sub-welcome", {})
                for recipient in removed_subscribers:
                    self.send_info_message([recipient], "unsub-goodbye", {})
                self.send_info_message(self.owners(), "setlist-done", {})

            self.moderation_box.remove(dict["id"])

    def obey_setlistsilentyes(self, dict):
        if self.moderation_box.has(dict["id"]):
            text = self.moderation_box.get(dict["id"])
            addresses = self.parse_setlist_addresses(text)
            if addresses == None:
                self.send_bad_addresses_in_setlist(id)
            else:
                self.subscribers.lock()
                old = self.subscribers.get_all()
                for address in old:
                    if address not in addresses:
                        self.subscribers.remove(address)
                    else:
                        addresses.remove(address)
                self.subscribers.add_many(addresses)
                self.subscribers.save()
                self.send_info_message(self.owners(), "setlist-done", {})

            self.moderation_box.remove(dict["id"])

    def obey_owner(self, text):
        sender = get_from_environ("SENDER")
        recipients = self.cp.get("list", "owners").split()
        self.mlm.send_mail(sender, recipients, text)

    def obey_subscribe_or_unsubscribe(self, dict, template_name, command, 
                                      origmail):

        requester  = get_from_environ("SENDER")
        subscriber = dict["sender"]
        if not subscriber:
            subscriber = requester
        if subscriber.find("@") == -1:
            info("Trying to (un)subscribe address without @: %s" % subscriber)
            return
        if self.cp.get("list", "ignore-bounce") == "yes":
            info("Will not (un)subscribe address: %s from static list" %subscriber)
            return
        if requester in self.owners():
            confirmers = self.owners()
        else:
            confirmers = [subscriber]

        id = self.subscription_box.add(subscriber, origmail)
        confirm = self.signed_address(command, id)
        self.send_info_message(confirmers, template_name,
                               {
                                    "confirm": confirm,
                                    "origmail": origmail,
                                    "boundary": self.invent_boundary(),
                               })

    def obey_subscribe(self, dict, origmail):
        self.obey_subscribe_or_unsubscribe(dict, "sub-confirm", "subyes", 
                                           origmail)

    def obey_unsubscribe(self, dict, origmail):
        self.obey_subscribe_or_unsubscribe(dict, "unsub-confirm", "unsubyes",
                                           origmail)

    def obey_subyes(self, dict):
        if self.subscription_box.has(dict["id"]):
            if self.cp.get("list", "subscription") == "free":
                recipient = self.subscription_box.get_address(dict["id"])
                self.subscribers.lock()
                self.subscribers.add(recipient)
                self.subscribers.save()
                sender = self.command_address("help")
                self.send_template(self.ignore(), sender, [recipient], 
                                   "sub-welcome", {})
                self.subscription_box.remove(dict["id"])
                if self.cp.get("list", "mail-on-subscription-changes")=="yes":
                    self.send_info_message(self.owners(), 
                                           "sub-owner-notification",
                                           {
                                            "address": recipient,
                                           })
            else:
                recipients = self.cp.get("list", "owners").split()
                confirm = self.signed_address("subapprove", dict["id"])
                deny = self.signed_address("subreject", dict["id"])
                subscriber = self.subscription_box.get_address(dict["id"])
                origmail = self.subscription_box.get(dict["id"])
                self.send_template(self.ignore(), deny, recipients, 
                                   "sub-moderate", 
                                   {
                                       "confirm": confirm,
                                       "deny": deny,
                                       "subscriber": subscriber,
                                       "origmail": origmail,
                                       "boundary": self.invent_boundary(),
                                   })
                recipient = self.subscription_box.get_address(dict["id"])
                self.send_info_message([recipient], "sub-wait", {})

    def obey_subapprove(self, dict):
        if self.subscription_box.has(dict["id"]):
            recipient = self.subscription_box.get_address(dict["id"])
            self.subscribers.lock()
            self.subscribers.add(recipient)
            self.subscribers.save()
            self.send_info_message([recipient], "sub-welcome", {})
            self.subscription_box.remove(dict["id"])
            if self.cp.get("list", "mail-on-subscription-changes")=="yes":
                self.send_info_message(self.owners(), "sub-owner-notification",
                                       {
                                        "address": recipient,
                                       })

    def obey_subreject(self, dict):
        if self.subscription_box.has(dict["id"]):
            recipient = self.subscription_box.get_address(dict["id"])
            self.send_info_message([recipient], "sub-reject", {})
            self.subscription_box.remove(dict["id"])

    def obey_unsubyes(self, dict):
        if self.subscription_box.has(dict["id"]):
            recipient = self.subscription_box.get_address(dict["id"])
            self.subscribers.lock()
            self.subscribers.remove(recipient)
            self.subscribers.save()
            self.send_info_message([recipient], "unsub-goodbye", {})
            self.subscription_box.remove(dict["id"])
            if self.cp.get("list", "mail-on-subscription-changes")=="yes":
                self.send_info_message(self.owners(),
                                       "unsub-owner-notification",
                                       {
                                        "address": recipient,
                                       })

    def store_into_archive(self, text):
        if self.cp.get("list", "archived") == "yes":
            archdir = os.path.join(self.dirname, "archive")
            if not os.path.exists(archdir):
                os.mkdir(archdir, 0700)
            id = md5sum_as_hex(text)
            f = open(os.path.join(archdir, id), "w")
            f.write(text)
            f.close()

    def list_headers(self):
        local, domain = self.name.split("@")
        list = []
        list.append("List-Id: <%s.%s>" % (local, domain))
        list.append("List-Help: <mailto:%s-help@%s>" % (local, domain))
        list.append("List-Unsubscribe: <mailto:%s-unsubscribe@%s>" % 
                    (local, domain))
        list.append("List-Subscribe: <mailto:%s-subscribe@%s>" % 
                    (local, domain))
        list.append("List-Post: <mailto:%s@%s>" % (local, domain))
        list.append("List-Owner: <mailto:%s-owner@%s>" % (local, domain))
        list.append("Precedence: bulk");
        return string.join(list, "\n") + "\n"

    def read_file(self, basename):
        try:
            f = open(os.path.join(self.dirname, basename), "r")
            data = f.read()
            f.close()
            return data
        except IOError:
            return ""

    def headers_to_add(self):
        headers_to_add = self.read_file("headers-to-add").rstrip()
        if headers_to_add:
            return headers_to_add + "\n"
        else:
            return ""

    def remove_some_headers(self, mail, headers_to_remove):
        endpos = mail.find("\n\n")
        if endpos == -1:
            endpos = mail.find("\n\r\n")
            if endpos == -1:
                return mail
        headers = mail[:endpos].split("\n")
        body = mail[endpos:]
        
        headers_to_remove = [x.lower() for x in headers_to_remove]
    
        remaining = []
        add_continuation_lines = 0

        for header in headers:
            if header[0] in [' ','\t']:
                # this is a continuation line
                if add_continuation_lines:
                    remaining.append(header)
            else:
                pos = header.find(":")
                if pos == -1:
                    # malformed message, try to remove the junk
                    add_continuation_lines = 0
                    continue
                name = header[:pos].lower()
                if name in headers_to_remove:
                    add_continuation_lines = 0
                else:
                    add_continuation_lines = 1
                    remaining.append(header)
        
        return "\n".join(remaining) + body

    def headers_to_remove(self, text):
        headers_to_remove = self.read_file("headers-to-remove").split("\n")
        headers_to_remove = map(lambda s: s.strip().lower(), 
                                headers_to_remove)
        return self.remove_some_headers(text, headers_to_remove)

    def append_footer(self, text):
        if "base64" in text or "BASE64" in text:
            import StringIO
            for line in StringIO.StringIO(text):
                if line.lower().startswith("content-transfer-encoding:") and \
                   "base64" in line.lower():
                    return text
        return text + self.template("footer", {})

    def send_mail_to_subscribers(self, text):
        text = self.remove_some_headers(text, ["list-id", "list-help",
                                               "list-unsubscribe",
                                               "list-subscribe", "list-post",
                                               "list-owner", "precedence"])
        text = self.headers_to_add() + self.list_headers() + \
               self.headers_to_remove(text)
        text = self.append_footer(text)
        text, = self.mlm.call_plugins("send_mail_to_subscribers_hook",
                                     self, text)
        if have_email_module and \
           self.cp.get("list", "pristine-headers") != "yes":
            text = self.mime_encode_headers(text)
        self.store_into_archive(text)
        for group in self.subscribers.groups():
            bounce = self.signed_address("bounce", group)
            addresses = self.subscribers.in_group(group)
            self.mlm.send_mail(bounce, addresses, text)

    def post_into_moderate(self, poster, dict, text):
        id = self.moderation_box.add(poster, text)
        recipients = self.moderators()
        if recipients == []:
            recipients = self.owners()

        confirm = self.signed_address("approve", id)
        deny = self.signed_address("reject", id)
        self.send_template(self.ignore(), deny, recipients, "msg-moderate",
                           {
                            "confirm": confirm,
                            "deny": deny,
                            "origmail": text,
                            "boundary": self.invent_boundary(),
                           })
        self.send_info_message([poster], "msg-wait", {})
    
    def should_be_moderated(self, posting, poster):
        if posting == "moderated":
            return 1
        if posting == "auto":
            if poster.lower() not in \
                map(string.lower, self.subscribers.get_all()):
                return 1
        return 0

    def obey_post(self, dict, text):
        if dict.has_key("force-moderation") and dict["force-moderation"]:
            force_moderation = 1
        else:
            force_moderation = 0
        if dict.has_key("force-posting") and dict["force-posting"]:
            force_posting = 1
        else:
            force_posting = 0
        posting = self.cp.get("list", "posting")
        if posting not in self.posting_opts:
            error("You have a weird 'posting' config. Please, review it")
        poster = get_from_environ("SENDER")
        if force_moderation:
            self.post_into_moderate(poster, dict, text)
        elif force_posting:
            self.send_mail_to_subscribers(text)
        elif self.should_be_moderated(posting, poster):
            self.post_into_moderate(poster, dict, text)
        else:
            self.send_mail_to_subscribers(text)
 
    def obey_approve(self, dict):
        if self.moderation_box.lock(dict["id"]):
            if self.moderation_box.has(dict["id"]):
                text = self.moderation_box.get(dict["id"])
                self.send_mail_to_subscribers(text)
                self.moderation_box.remove(dict["id"])
            self.moderation_box.unlock(dict["id"])

    def obey_reject(self, dict):
        if self.moderation_box.lock(dict["id"]):
            if self.moderation_box.has(dict["id"]):
                self.moderation_box.remove(dict["id"])
            self.moderation_box.unlock(dict["id"])

    def split_address_list(self, addrs):
        domains = {}
        for addr in addrs:
            userpart, domain = addr.split("@")
            if domains.has_key(domain):
                domains[domain].append(addr)
            else:
                domains[domain] = [addr]
        result = []
        if len(domains.keys()) == 1:
            for addr in addrs:
                result.append([addr])
        else:
            result = domains.values()
        return result

    def obey_bounce(self, dict, text):
        if self.subscribers.has_group(dict["id"]):
            self.subscribers.lock()
            addrs = self.subscribers.in_group(dict["id"])
            if len(addrs) == 1:
                if self.cp.get("list", "ignore-bounce") == "yes":
                    info("Address <%s> bounced, ignoring bounce as configured." %
                         addrs[0])
                    self.subscribers.unlock()
                    return
                debug("Address <%s> bounced, setting state to bounce." %
                      addrs[0])
                bounce_id = self.bounce_box.add(addrs[0], text[:4096])
                self.subscribers.set(dict["id"], "status", "bounced")
                self.subscribers.set(dict["id"], "timestamp-bounced", 
                                     "%f" % time.time())
                self.subscribers.set(dict["id"], "bounce-id",
                                     bounce_id)
            else:
                debug("Group %s bounced, splitting." % dict["id"])
                for new_addrs in self.split_address_list(addrs):
                    self.subscribers.add_many(new_addrs)
                self.subscribers.remove_group(dict["id"])
            self.subscribers.save()
        else:
            debug("Ignoring bounce, group %s doesn't exist (anymore?)." %
                  dict["id"])

    def obey_probe(self, dict, text):
        id = dict["id"]
        if self.subscribers.has_group(id):
            self.subscribers.lock()
            if self.subscribers.get(id, "status") == "probed":
                self.subscribers.set(id, "status", "probebounced")
            self.subscribers.save()

    def obey(self, dict):
        text = self.read_stdin()

        if dict["command"] in ["help", "list", "subscribe", "unsubscribe",
                               "subyes", "subapprove", "subreject",
                               "unsubyes", "post", "approve"]:
            sender = get_from_environ("SENDER")
            if not sender:
                debug("Ignoring bounce message for %s command." % 
                        dict["command"])
                return

        if dict["command"] == "help":
            self.obey_help()
        elif dict["command"] == "list":
            self.obey_list()
        elif dict["command"] == "owner":
            self.obey_owner(text)
        elif dict["command"] == "subscribe":
            self.obey_subscribe(dict, text)
        elif dict["command"] == "unsubscribe":
            self.obey_unsubscribe(dict, text)
        elif dict["command"] == "subyes":
            self.obey_subyes(dict)
        elif dict["command"] == "subapprove":
            self.obey_subapprove(dict)
        elif dict["command"] == "subreject":
            self.obey_subreject(dict)
        elif dict["command"] == "unsubyes":
            self.obey_unsubyes(dict)
        elif dict["command"] == "post":
            self.obey_post(dict, text)
        elif dict["command"] == "approve":
            self.obey_approve(dict)
        elif dict["command"] == "reject":
            self.obey_reject(dict)
        elif dict["command"] == "bounce":
            self.obey_bounce(dict, text)
        elif dict["command"] == "probe":
            self.obey_probe(dict, text)
        elif dict["command"] == "setlist":
            self.obey_setlist(text)
        elif dict["command"] == "setlistsilently":
            self.obey_setlistsilently(text)
        elif dict["command"] == "setlistyes":
            self.obey_setlistyes(dict)
        elif dict["command"] == "setlistsilentyes":
            self.obey_setlistsilentyes(dict)
        elif dict["command"] == "ignore":
            pass

    def get_bounce_text(self, id):
        bounce_id = self.subscribers.get(id, "bounce-id")
        if self.bounce_box.has(bounce_id):
            bounce_text = self.bounce_box.get(bounce_id)
            bounce_text = string.join(map(lambda s: "> " + s + "\n",
                                          bounce_text.split("\n")), "")
        else:
            bounce_text = "Bounce message not available."
        return bounce_text

    one_week = 7.0 * 24.0 * 60.0 * 60.0

    def handle_bounced_groups(self, now):
        for id in self.subscribers.groups():
            status = self.subscribers.get(id, "status") 
            t = float(self.subscribers.get(id, "timestamp-bounced")) 
            if status == "bounced":
                if now - t > self.one_week:
                    sender = self.signed_address("probe", id) 
                    recipients = self.subscribers.in_group(id) 
                    self.send_template(sender, sender, recipients,
                                       "bounce-warning", {
                                        "bounce": self.get_bounce_text(id),
                                        "boundary": self.invent_boundary(),
                                       })
                    self.subscribers.set(id, "status", "probed")
            elif status == "probed":
                if now - t > 2 * self.one_week:
                    debug(("Cleaning woman: probe didn't bounce " + 
                          "for group <%s>, setting status to ok.") % id)
                    self.subscribers.set(id, "status", "ok")
                    self.bounce_box.remove(
                            self.subscribers.get(id, "bounce-id"))
            elif status == "probebounced":
                sender = self.command_address("help") 
                for address in self.subscribers.in_group(id):
                    if self.cp.get("list", "mail-on-forced-unsubscribe") \
                        == "yes":
                        self.send_template(sender, sender,
                                       self.owners(),
                                       "bounce-owner-notification",
                                       {
                                        "address": address,
                                        "bounce": self.get_bounce_text(id),
                                        "boundary": self.invent_boundary(),
                                       })

                    self.bounce_box.remove(
                            self.subscribers.get(id, "bounce-id"))
                    self.subscribers.remove(address) 
                    debug("Cleaning woman: removing <%s>." % address)
                    self.send_template(sender, sender, [address],
                                       "bounce-goodbye", {})

    def join_nonbouncing_groups(self, now):
        to_be_joined = []
        for id in self.subscribers.groups():
            status = self.subscribers.get(id, "status")
            age1 = now - float(self.subscribers.get(id, "timestamp-bounced"))
            age2 = now - float(self.subscribers.get(id, "timestamp-created"))
            if status == "ok":
                if age1 > self.one_week and age2 > self.one_week:
                    to_be_joined.append(id)
        if to_be_joined:
            addrs = []
            for id in to_be_joined:
                addrs = addrs + self.subscribers.in_group(id)
            self.subscribers.add_many(addrs)
            for id in to_be_joined:
                self.bounce_box.remove(self.subscribers.get(id, "bounce-id"))
                self.subscribers.remove_group(id)

    def remove_empty_groups(self):
        for id in self.subscribers.groups()[:]:
            if len(self.subscribers.in_group(id)) == 0:
                self.subscribers.remove_group(id)

    def cleaning_woman(self, now):
        if self.subscribers.lock():
            self.handle_bounced_groups(now)
            self.join_nonbouncing_groups(now)
            self.subscribers.save()

class SubscriberDatabase:

    def __init__(self, dirname, name):
        self.dict = {}
        self.filename = os.path.join(dirname, name)
        self.lockname = os.path.join(dirname, "lock")
        self.loaded = 0
        self.locked = 0

    def lock(self):
        if os.system("lockfile -l 60 %s" % self.lockname) == 0:
            self.locked = 1
            self.load()
        return self.locked
    
    def unlock(self):
        os.remove(self.lockname)
        self.locked = 0
    
    def load(self):
        if not self.loaded and not self.dict:
            f = open(self.filename, "r")
            for line in f.xreadlines():
                parts = line.split()
                self.dict[parts[0]] = {
                    "status": parts[1],
                    "timestamp-created": parts[2],
                    "timestamp-bounced": parts[3],
                    "bounce-id": parts[4],
                    "addresses": parts[5:],
                }
            f.close()
            self.loaded = 1

    def save(self):
        assert self.locked
        assert self.loaded
        f = open(self.filename + ".new", "w")
        for id in self.dict.keys():
            f.write("%s " % id)
            f.write("%s " % self.dict[id]["status"])
            f.write("%s " % self.dict[id]["timestamp-created"])
            f.write("%s " % self.dict[id]["timestamp-bounced"])
            f.write("%s " % self.dict[id]["bounce-id"])
            f.write("%s\n" % string.join(self.dict[id]["addresses"], " "))
        f.close()
        os.remove(self.filename)
        os.rename(self.filename + ".new", self.filename)
        self.unlock()

    def get(self, id, attribute):
        self.load()
        if self.dict.has_key(id) and self.dict[id].has_key(attribute):
            return self.dict[id][attribute]
        return None

    def set(self, id, attribute, value):
        assert self.locked
        self.load()
        if self.dict.has_key(id) and self.dict[id].has_key(attribute):
            self.dict[id][attribute] = value

    def add(self, address):
        return self.add_many([address])

    def add_many(self, addresses):
        assert self.locked
        assert self.loaded
        for addr in addresses[:]:
            if addr.find("@") == -1:
                info("Address '%s' does not contain an @, ignoring it." % addr)
                addresses.remove(addr)
        for id in self.dict.keys():
            old_ones = self.dict[id]["addresses"]
            for addr in addresses:
                for x in old_ones:
                    if x.lower() == addr.lower():
                        old_ones.remove(x)
            self.dict[id]["addresses"] = old_ones
        id = self.new_group()
        self.dict[id] = {
            "status": "ok",
            "timestamp-created": self.timestamp(),
            "timestamp-bounced": "0",
            "bounce-id": "..notexist..",
            "addresses": addresses,
        }
        return id

    def new_group(self):
        keys = self.dict.keys()
        if keys:
            keys = map(lambda x: int(x), keys)
            keys.sort()
            return "%d" % (keys[-1] + 1)
        else:
            return "0"

    def timestamp(self):
        return "%.0f" % time.time()

    def get_all(self):
        self.load()
        list = []
        for values in self.dict.values():
            list = list + values["addresses"]
        return list

    def groups(self):
        self.load()
        return self.dict.keys()

    def has_group(self, id):
        self.load()
        return self.dict.has_key(id)

    def in_group(self, id):
        self.load()
        return self.dict[id]["addresses"]

    def remove(self, address):
        assert self.locked
        self.load()
        for id in self.dict.keys():
            group = self.dict[id]
            for x in group["addresses"][:]:
                if x.lower() == address.lower():
                    group["addresses"].remove(x)
                    if len(group["addresses"]) == 0:
                        del self.dict[id]

    def remove_group(self, id):
        assert self.locked
        self.load()
        del self.dict[id]


class MessageBox:

    def __init__(self, dirname, boxname):
        self.boxdir = os.path.join(dirname, boxname)
        if not os.path.isdir(self.boxdir):
            os.mkdir(self.boxdir, 0700)

    def filename(self, id):
        return os.path.join(self.boxdir, id)

    def add(self, address, message_text):
        id = self.make_id(message_text)
        filename = self.filename(id)
        f = open(filename + ".address", "w")
        f.write(address)
        f.close()
        f = open(filename + ".new", "w")
        f.write(message_text)
        f.close()
        os.rename(filename + ".new", filename)
        return id

    def make_id(self, message_text):
        return md5sum_as_hex(message_text)
        # XXX this might be unnecessarily long

    def remove(self, id):
        filename = self.filename(id)
        if os.path.isfile(filename):
            os.remove(filename)
            os.remove(filename + ".address")

    def has(self, id):
        return os.path.isfile(self.filename(id))

    def get_address(self, id):
        f = open(self.filename(id) + ".address", "r")
        data = f.read()
        f.close()
        return data.strip()

    def get(self, id):
        f = open(self.filename(id), "r")
        data = f.read()
        f.close()
        return data

    def lockname(self, id):
        return self.filename(id) + ".lock"

    def lock(self, id):
        if os.system("lockfile -l 600 %s" % self.lockname(id)) == 0:
            return 1
        else:
            return 0
    
    def unlock(self, id):
        try:
            os.remove(self.lockname(id))
        except os.error:
            pass
    


class DevNull:

    def write(self, str):
        pass


log_file_handle = None
def log_file():
    global log_file_handle
    if log_file_handle is None:
        try:
            log_file_handle = open(os.path.join(DOTDIR, "logfile.txt"), "a")
        except:
            log_file_handle = DevNull()
    return log_file_handle

def timestamp():
    tuple = time.localtime(time.time())
    return time.strftime("%Y-%m-%d %H:%M:%S", tuple) + " [%d]" % os.getpid()


quiet = 0


# No logging to stderr of debug messages. Some MTAs have a limit on how
# much data they accept via stderr and debug logs will fill that quickly.
def debug(msg):
    log_file().write(timestamp() + " " + msg + "\n")


# Log to log file first, in case MTA's stderr buffer fills up and we lose
# logs.
def info(msg):
    log_file().write(timestamp() + " " + msg + "\n")
    sys.stderr.write(msg + "\n")


def error(msg):
    info(msg)
    sys.exit(1)


def usage():
    sys.stdout.write("""\
Usage: enemies-of-carlotta [options] command
Mailing list manager.

Options:
  --name=listname@domain
  --owner=address@domain
  --moderator=address@domain
  --subscription=free/moderated
  --posting=free/moderated/auto
  --archived=yes/no
  --ignore-bounce=yes/no
  --language=language code or empty
  --mail-on-forced-unsubscribe=yes/no
  --mail-on-subscription-changes=yes/no
  --skip-prefix=string
  --domain=domain.name
  --smtp-server=domain.name
  --quiet
  --moderate

Commands:
  --help
  --create
  --subscribe
  --unsubscribe
  --list
  --is-list
  --edit
  --incoming
  --cleaning-woman
  --show-lists

For more detailed information, please read the enemies-of-carlotta(1)
manual page.
""")
    sys.exit(0)


def no_act_send_mail(sender, recipients, text):
    print "NOT SENDING MAIL FOR REAL!"
    print "Sender:", sender
    print "Recipients:", recipients
    print "Mail:"
    print "\n".join(map(lambda s: "   " + s, text.split("\n")))


def set_list_options(list, owners, moderators, subscription, posting, 
                     archived, language, ignore_bounce,
                     mail_on_sub_changes, mail_on_forced_unsub):
    if owners:
        list.cp.set("list", "owners", string.join(owners, " "))
    if moderators:
        list.cp.set("list", "moderators", string.join(moderators, " "))
    if subscription != None:
        list.cp.set("list", "subscription", subscription)
    if posting != None:
        list.cp.set("list", "posting", posting)
    if archived != None:
        list.cp.set("list", "archived", archived)
    if language != None:
        list.cp.set("list", "language", language)
    if ignore_bounce != None:
        list.cp.set("list", "ignore-bounce", ignore_bounce)
    if mail_on_sub_changes != None:
        list.cp.set("list", "mail-on-subscription-changes", 
                            mail_on_sub_changes)
    if mail_on_forced_unsub != None:
        list.cp.set("list", "mail-on-forced-unsubscribe",
                            mail_on_forced_unsub)


def main(args):
    try:
        opts, args = getopt.getopt(args, "h",
                                   ["name=",
                                    "owner=",
                                    "moderator=",
                                    "subscription=",
                                    "posting=",
                                    "archived=",
                                    "language=",
                                    "ignore-bounce=",
                                    "mail-on-forced-unsubscribe=",
                                    "mail-on-subscription-changes=",
                                    "skip-prefix=",
                                    "domain=",
                                    "sendmail=",
                                    "smtp-server=",
                                    "qmqp-server=",
                                    "quiet",
                                    "moderate",
                                    "post",
                                    "sender=",
                                    "recipient=",
                                    "no-act",
                                    
                                    "set",
                                    "get",
                                    "help",
                                    "create",
                                    "destroy",
                                    "subscribe",
                                    "unsubscribe",
                                    "list",
                                    "is-list",
                                    "edit",
                                    "incoming",
                                    "cleaning-woman",
                                    "show-lists",
                                    "version",
                                   ])
    except getopt.GetoptError, detail:
        error("Error parsing command line options (see --help):\n%s" % 
              detail)

    operation = None
    list_name = None
    owners = []
    moderators = []
    subscription = None
    posting = None
    archived = None
    ignore_bounce = None
    skip_prefix = None
    domain = None
    sendmail = "/usr/sbin/sendmail"
    smtp_server = None
    qmqp_server = None
    moderate = 0
    post = 0
    sender = None
    recipient = None
    language = None
    mail_on_forced_unsub = None
    mail_on_sub_changes = None
    no_act = 0
    global quiet

    for opt, arg in opts:
        if opt == "--name":
            list_name = arg
        elif opt == "--owner":
            owners.append(arg)
        elif opt == "--moderator":
            moderators.append(arg)
        elif opt == "--subscription":
            subscription = arg
        elif opt == "--posting":
            posting = arg
        elif opt == "--archived":
            archived = arg
        elif opt == "--ignore-bounce":
            ignore_bounce = arg
        elif opt == "--skip-prefix":
            skip_prefix = arg
        elif opt == "--domain":
            domain = arg
        elif opt == "--sendmail":
            sendmail = arg
        elif opt == "--smtp-server":
            smtp_server = arg
        elif opt == "--qmqp-server":
            qmqp_server = arg
        elif opt == "--sender":
            sender = arg
        elif opt == "--recipient":
            recipient = arg
        elif opt == "--language":
            language = arg
        elif opt == "--mail-on-forced-unsubscribe":
            mail_on_forced_unsub = arg
        elif opt == "--mail-on-subscription-changes":
            mail_on_sub_changes = arg
        elif opt == "--moderate":
            moderate = 1
        elif opt == "--post":
            post = 1
        elif opt == "--quiet":
            quiet = 1
        elif opt == "--no-act":
            no_act = 1
        else:
            operation = opt

    if operation is None:
        error("No operation specified, see --help.")

    if list_name is None and operation not in ["--incoming", "--help", "-h",
                                               "--cleaning-woman",
                                               "--show-lists",
                                               "--version"]:
        error("%s requires a list name specified with --name" % operation)

    if operation in ["--help", "-h"]:
        usage()

    if sender or recipient:
        environ = os.environ.copy()
        if sender:
            environ["SENDER"] = sender
        if recipient:
            environ["RECIPIENT"] = recipient
        set_environ(environ)

    mlm = MailingListManager(DOTDIR, sendmail=sendmail, 
                             smtp_server=smtp_server,
                             qmqp_server=qmqp_server)
    if no_act:
        mlm.send_mail = no_act_send_mail

    if operation == "--create":
        if not owners:
            error("You must give at least one list owner with --owner.")
        list = mlm.create_list(list_name)
        set_list_options(list, owners, moderators, subscription, posting, 
                         archived, language, ignore_bounce,
                         mail_on_sub_changes, mail_on_forced_unsub)
        list.save_config()
        debug("Created list %s." % list_name)
    elif operation == "--destroy":
        shutil.rmtree(os.path.join(DOTDIR, list_name))
        debug("Removed list %s." % list_name)
    elif operation == "--edit":
        list = mlm.open_list(list_name)
        set_list_options(list, owners, moderators, subscription, posting, 
                         archived, language, ignore_bounce,
                         mail_on_sub_changes, mail_on_forced_unsub)
        list.save_config()
    elif operation == "--subscribe":
        list = mlm.open_list(list_name)
        list.subscribers.lock()
        for address in args:
            if address.find("@") == -1:
                error("Address '%s' does not contain an @." % address)
            list.subscribers.add(address)
            debug("Added subscriber <%s>." % address)
        list.subscribers.save()
    elif operation == "--unsubscribe":
        list = mlm.open_list(list_name)
        list.subscribers.lock()
        for address in args:
            list.subscribers.remove(address)
            debug("Removed subscriber <%s>." % address)
        list.subscribers.save()
    elif operation == "--list":
        list = mlm.open_list(list_name)
        for address in list.subscribers.get_all():
            print address
    elif operation == "--is-list":
        if mlm.is_list(list_name, skip_prefix, domain):
            debug("Indeed a mailing list: <%s>" % list_name)
        else:
            debug("Not a mailing list: <%s>" % list_name)
            sys.exit(1)
    elif operation == "--incoming":
        mlm.incoming_message(skip_prefix, domain, moderate, post)
    elif operation == "--cleaning-woman":
        mlm.cleaning_woman()
    elif operation == "--show-lists":
        listnames = mlm.get_lists()
        listnames.sort()
        for listname in listnames:
            print listname
    elif operation == "--get":
        list = mlm.open_list(list_name)
        for name in args:
            print list.cp.get("list", name)
    elif operation == "--set":
        list = mlm.open_list(list_name)
        for arg in args:
            if "=" not in arg:
                error("Error: --set arguments must be of form name=value")
            name, value = arg.split("=", 1)
            list.cp.set("list", name, value)
        list.save_config()
    elif operation == "--version":
        print "EoC, version %s" % VERSION
        print "Home page: http://liw.iki.fi/liw/eoc/"
    else:
        error("Internal error: unimplemented option <%s>." % operation)

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except EocException, detail:
        error("Error: %s" % detail)
