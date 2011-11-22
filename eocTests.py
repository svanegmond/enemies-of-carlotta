import unittest
import shutil
import os
import re
import time
import string

import eoc

DOTDIR = "dot-dir-for-testing"
eoc.DOTDIR = DOTDIR
eoc.quiet = 1

def no_op(*args):
    pass

class AddressCleaningTestCases(unittest.TestCase):

    def setUp(self):
        self.ap = eoc.AddressParser(["foo@EXAMPLE.com",
                                     "bar@lists.example.com"])
    
    def verify(self, address, wanted, skip_prefix=None, forced_domain=None):
        self.ap.set_skip_prefix(skip_prefix)
        self.ap.set_forced_domain(forced_domain)
        address = self.ap.clean(address)
        self.failUnlessEqual(address, wanted)
    
    def testSimpleAddress(self):
        self.verify("foo@example.com", "foo@example.com")

    def testUpperCaseAddress(self):
        self.verify("FOO@EXAMPLE.COM", "foo@example.com")

    def testPrefixRemoval(self):
        self.verify("foo@example.com", "foo@example.com", 
                    skip_prefix="user-")
        self.verify("user-foo@example.com", "foo@example.com", 
                    skip_prefix="user-")

    def testForcedDomain(self):
        self.verify("foo@example.com", "foo@example.com",
                    forced_domain="example.com")
        self.verify("foo@whatever.example.com", "foo@example.com", 
                    forced_domain="example.com")

    def testPrefixRemovalWithForcedDomain(self):
        self.verify("foo@example.com", "foo@example.com", 
                    skip_prefix="user-",
                    forced_domain="example.com")
        self.verify("foo@whatever.example.com", "foo@example.com", 
                    skip_prefix="user-",
                    forced_domain="example.com")
        self.verify("user-foo@example.com", "foo@example.com", 
                    skip_prefix="user-",
                    forced_domain="example.com")
        self.verify("user-foo@whatever.example.com", "foo@example.com", 
                    skip_prefix="user-",
                    forced_domain="example.com")

class AddressParserTestCases(unittest.TestCase):

    def setUp(self):
        self.ap = eoc.AddressParser(["foo@EXAMPLE.com",
                                     "bar@lists.example.com"])
    
    def verify_parser(self, address, wanted_listname, wanted_parts):
        listname, parts = self.ap.parse(address)
        self.failUnlessEqual(listname, wanted_listname)
        self.failUnlessEqual(parts, wanted_parts)
        
    def testParser(self):
        self.verify_parser("foo@example.com", 
                           "foo@EXAMPLE.com", 
                           [])
        self.verify_parser("foo-subscribe@example.com", 
                           "foo@EXAMPLE.com", 
                           ["subscribe"])
        self.verify_parser("foo-subscribe-joe=example.com@example.com", 
                           "foo@EXAMPLE.com", 
                           ["subscribe", "joe=example.com"])
        self.verify_parser("foo-bounce-123-ABCDEF@example.com", 
                           "foo@EXAMPLE.com", 
                           ["bounce", "123", "abcdef"])

class ParseRecipientAddressBase(unittest.TestCase):

    def setUp(self):
        self.lists = ["foo@example.com", 
                      "bar@lists.example.com",
                      "foo-announce@example.com"]
        self.mlm = eoc.MailingListManager(DOTDIR, lists=self.lists)
    
    def environ(self, sender, recipient):
        eoc.set_environ({
            "SENDER": sender,
            "RECIPIENT": recipient,
        })

class ParseUnsignedAddressTestCases(ParseRecipientAddressBase):

    def testEmpty(self):
        self.failUnlessRaises(eoc.UnknownList,
                              self.mlm.parse_recipient_address, 
                              "", None, None)

    def verify(self, address, skip_prefix, forced_domain, wanted_dict):
        dict = self.mlm.parse_recipient_address(address, skip_prefix, 
                                                forced_domain)
        self.failUnlessEqual(dict, wanted_dict)

    def testSimpleAddresses(self):
        self.verify("foo@example.com", 
                    None, 
                    None, 
                    { "name": "foo@example.com", "command": "post" })
        self.verify("FOO@EXAMPLE.COM", 
                    None, 
                    None, 
                    { "name": "foo@example.com", "command": "post" })
        self.verify("prefix-foo@example.com", 
                    "prefix-", 
                    None, 
                    { "name": "foo@example.com", "command": "post" })
        self.verify("bar@example.com", 
                    None, 
                    "lists.example.com", 
                    { "name": "bar@lists.example.com", "command": "post" })
        self.verify("prefix-bar@example.com", 
                    "prefix-",
                    "lists.example.com", 
                    { "name": "bar@lists.example.com", "command": "post" })

    def testSubscription(self):
        self.verify("foo-subscribe@example.com", 
                    None,
                    None,
                    { "name": "foo@example.com", 
                      "command": "subscribe",
                      "sender": "",
                    })
        self.verify("foo-subscribe-joe-user=example.com@example.com", 
                    None,
                    None,
                    { "name": "foo@example.com", 
                      "command": "subscribe",
                      "sender": "joe-user@example.com",
                    })
        self.verify("foo-unsubscribe@example.com", 
                    None,
                    None,
                    { "name": "foo@example.com", 
                      "command": "unsubscribe",
                      "sender": "",
                    })
        self.verify("foo-unsubscribe-joe-user=example.com@example.com", 
                    None,
                    None,
                    { "name": "foo@example.com", 
                      "command": "unsubscribe",
                      "sender": "joe-user@example.com",
                    })

    def testPost(self):
        for name in self.lists:
            self.verify(name, None, None, { "name": name, "command": "post" })

    def testSimpleCommands(self):
        for name in self.lists:
            for command in ["help", "list", "owner"]:
                localpart, domain = name.split("@")
                address = "%s-%s@%s" % (localpart, command, domain)
                self.verify(address, None, None,
                            { "name": name,
                              "command": command
                            })

class ParseWellSignedAddressTestCases(ParseRecipientAddressBase):

    def try_good_signature(self, command):
        s = "foo-announce-%s-1" % command
        hash = self.mlm.compute_hash("%s@%s" % (s, "example.com"))
        local_part = "%s-%s" % (s, hash)
        dict = self.mlm.parse_recipient_address("%s@example.com" % local_part,
                                                None, None)
        self.failUnlessEqual(dict,
                             {
                                "name": "foo-announce@example.com",
                                "command": command,
                                "id": "1",
                             })

    def testProperlySignedCommands(self):
        self.try_good_signature("subyes")
        self.try_good_signature("subapprove")
        self.try_good_signature("subreject")
        self.try_good_signature("unsubyes")
        self.try_good_signature("bounce")
        self.try_good_signature("approve")
        self.try_good_signature("reject")
        self.try_good_signature("probe")

class ParseBadlySignedAddressTestCases(ParseRecipientAddressBase):

    def try_bad_signature(self, command_part):
        self.failUnlessRaises(eoc.BadSignature,
                              self.mlm.parse_recipient_address, 
                              "foo-announce-" + command_part + 
                                    "-123-badhash@example.com",
                              None, None)

    def testBadlySignedCommands(self):
        self.try_bad_signature("subyes")
        self.try_bad_signature("subapprove")
        self.try_bad_signature("subreject")
        self.try_bad_signature("unsubyes")
        self.try_bad_signature("bounce")
        self.try_bad_signature("approve")
        self.try_bad_signature("reject")
        self.try_bad_signature("probe")

class DotDirTestCases(unittest.TestCase):

    def setUp(self):
        self.secret_name = os.path.join(DOTDIR, "secret")

    def tearDown(self):
        shutil.rmtree(DOTDIR)

    def dotdir_is_ok(self):
        self.failUnless(os.path.isdir(DOTDIR))
        self.failUnless(os.path.isfile(self.secret_name))

    def testNoDotDirExists(self):
        self.failIf(os.path.exists(DOTDIR))
        mlm = eoc.MailingListManager(DOTDIR)
        self.dotdir_is_ok()

    def testDotDirDoesExistButSecretDoesNot(self):
        self.failIf(os.path.exists(DOTDIR))
        os.makedirs(DOTDIR)
        self.failUnless(os.path.isdir(DOTDIR))
        self.failIf(os.path.exists(self.secret_name))
        mlm = eoc.MailingListManager(DOTDIR)
        self.dotdir_is_ok()


class RemoveSomeHeadersTest(unittest.TestCase):

    def testRemoveSomeHeaders(self):
        mlm = eoc.MailingListManager(DOTDIR)
        ml = eoc.MailingList(mlm, "list@example.com")
        mail = """\
Header-1: this is a simple header
Header-2: this
    is
    a
    complex header with a colon: yes it is
Header-3: odd numbered headers are simple

Body.
"""
        mail2 = ml.remove_some_headers(mail, ["Header-2"])
        self.failUnlessEqual(mail2, """\
Header-1: this is a simple header
Header-3: odd numbered headers are simple

Body.
""")

class ListBase(unittest.TestCase):

    def setUp(self):
        if os.path.exists(DOTDIR):
            shutil.rmtree(DOTDIR)
        self.mlm = eoc.MailingListManager(DOTDIR)

    def tearDown(self):
        self.mlm = None
        shutil.rmtree(DOTDIR)

class ListCreationTestCases(ListBase):

    def setUp(self):
        ListBase.setUp(self)
        self.names = None

    def listdir(self, listname):
        return os.path.join(DOTDIR, listname)

    def listdir_has_file(self, listdir, filename):
        self.failUnless(os.path.isfile(os.path.join(listdir, filename)))
        self.names.remove(filename)

    def listdir_has_dir(self, listdir, dirname):
        self.failUnless(os.path.isdir(os.path.join(listdir, dirname)))
        self.names.remove(dirname)

    def listdir_may_have_dir(self, listdir, dirname):
        if dirname in self.names:
            self.listdir_has_dir(listdir, dirname)

    def listdir_is_ok(self, listname):
        listdir = self.listdir(listname)
        self.failUnless(os.path.isdir(listdir))
        self.names = os.listdir(listdir)
        
        self.listdir_has_file(listdir, "config")
        self.listdir_has_file(listdir, "subscribers")
            
        self.listdir_has_dir(listdir, "bounce-box")
        self.listdir_has_dir(listdir, "subscription-box")
            
        self.listdir_may_have_dir(listdir, "moderation-box")
        self.listdir_may_have_dir(listdir, "templates")
            
        # Make sure there are no extras.
        self.failUnlessEqual(self.names, [])

    def testCreateNew(self):
        self.failIf(os.path.exists(self.listdir("foo@example.com")))
        ml = self.mlm.create_list("foo@example.com")

        self.failUnlessEqual(ml.__class__, eoc.MailingList)
        self.failUnlessEqual(ml.dirname, self.listdir("foo@example.com"))

        self.listdir_is_ok("foo@example.com")

    def testCreateExisting(self):
        list = self.mlm.create_list("foo@example.com")
        self.failUnlessRaises(eoc.ListExists,
                              self.mlm.create_list, "foo@example.com")
        self.listdir_is_ok("foo@example.com")

class ListOptionTestCases(ListBase):

    def check(self, ml, wanted):
        self.failUnlessEqual(ml.cp.sections(), ["list"])
        cpdict = {}
        for key, value in ml.cp.items("list"):
            cpdict[key] = value
        self.failUnlessEqual(cpdict, wanted)

    def testDefaultOptionsOnCreateAndOpenExisting(self):
        self.mlm.create_list("foo@example.com")
        ml = self.mlm.open_list("foo@example.com")
        self.check(ml,
                   {
                      "owners": "",
                      "moderators": "",
                      "subscription": "free",
                      "posting": "free",
                      "archived": "no",
                      "mail-on-subscription-changes": "no",
                      "mail-on-forced-unsubscribe": "no",
                      "ignore-bounce": "no",
                      "language": "",
                      "pristine-headers": "",
                   })

    def testChangeOptions(self):
        # Create a list, change some options, and save the result.
        ml = self.mlm.create_list("foo@example.com")
        self.failUnlessEqual(ml.cp.get("list", "owners"), "")
        self.failUnlessEqual(ml.cp.get("list", "posting"), "free")
        ml.cp.set("list", "owners", "owner@example.com")
        ml.cp.set("list", "posting", "moderated")
        ml.save_config()
        
        # Re-open the list and check that the new instance has read the
        # values from the disk correctly.
        ml2 = self.mlm.open_list("foo@example.com")
        self.check(ml2,
                   {
                      "owners": "owner@example.com",
                      "moderators": "",
                      "subscription": "free",
                      "posting": "moderated",
                      "archived": "no",
                      "mail-on-subscription-changes": "no",
                      "mail-on-forced-unsubscribe": "no",
                      "ignore-bounce": "no",
                      "language": "",
                      "pristine-headers": "",
                   })

class SubscriberDatabaseTestCases(ListBase):

    def has_subscribers(self, ml, addrs):
        subs = ml.subscribers.get_all()
        subs.sort()
        self.failUnlessEqual(subs, addrs)

    def testAddAndRemoveSubscribers(self):
        addrs = ["joe@example.com", "MARY@example.com", "bubba@EXAMPLE.com"]
        addrs.sort()
    
        ml = self.mlm.create_list("foo@example.com")
        self.failUnlessEqual(ml.subscribers.get_all(), [])

        self.failUnless(ml.subscribers.lock())
        ml.subscribers.add_many(addrs)
        self.has_subscribers(ml, addrs)
        ml.subscribers.save()
        self.failIf(ml.subscribers.locked)
        ml = None

        ml2 = self.mlm.open_list("foo@example.com")
        self.has_subscribers(ml2, addrs)
        ml2.subscribers.lock()
        ml2.subscribers.remove(addrs[0])
        self.has_subscribers(ml2, addrs[1:])
        
        ml2.subscribers.save()
        
        ml3 = self.mlm.open_list("foo@example.com")
        self.has_subscribers(ml3, addrs[1:])

    def testSubscribeTwice(self):
        ml = self.mlm.create_list("foo@example.com")
        self.failUnlessEqual(ml.subscribers.get_all(), [])
        ml.subscribers.lock()
        ml.subscribers.add("user@example.com")
        ml.subscribers.add("USER@example.com")
        self.failUnlessEqual(map(string.lower, ml.subscribers.get_all()),
                             map(string.lower, ["USER@example.com"]))

    def testSubscriberAttributesAndGroups(self):
        addrs = ["joe@example.com", "mary@example.com"]
        addrs.sort()
        ml = self.mlm.create_list("foo@example.com")
        self.failUnlessEqual(ml.subscribers.groups(), [])
        ml.subscribers.lock()
        id = ml.subscribers.add_many(addrs)
        self.failUnlessEqual(ml.subscribers.groups(), ["0"])
        self.failUnlessEqual(ml.subscribers.get(id, "status"), "ok")
        ml.subscribers.set(id, "status", "bounced")
        self.failUnlessEqual(ml.subscribers.get(id, "status"), "bounced")
        subs = ml.subscribers.in_group(id)
        subs.sort()
        self.failUnlessEqual(subs, addrs)

class ModerationBoxTestCases(ListBase):

    def testModerationBox(self):
        ml = self.mlm.create_list("foo@example.com")
        listdir = os.path.join(DOTDIR, "foo@example.com")
        boxdir = os.path.join(listdir, "moderation-box")

        self.failUnlessEqual(boxdir, ml.moderation_box.boxdir)
        self.failUnless(os.path.isdir(boxdir))

        mailtext = "From: foo\nTo: bar\n\nhello\n"
        id = ml.moderation_box.add("foo", mailtext)
        self.failUnless(ml.moderation_box.has(id))
        self.failUnlessEqual(ml.moderation_box.get_address(id), "foo")
        self.failUnlessEqual(ml.moderation_box.get(id), mailtext)
        
        filename = os.path.join(boxdir, id)
        self.failUnless(os.path.isfile(filename))
        self.failUnless(os.path.isfile(filename + ".address"))
        
        ml.moderation_box.remove(id)
        self.failIf(ml.moderation_box.has(id))
        self.failUnless(not os.path.exists(filename))

class IncomingBase(unittest.TestCase):

    def setUp(self):
        if os.path.isdir(DOTDIR):
            shutil.rmtree(DOTDIR)
        self.mlm = eoc.MailingListManager(DOTDIR)
        self.ml = None
        ml = self.mlm.create_list("foo@EXAMPLE.com")
        ml.cp.set("list", "owners", "listmaster@example.com")
        ml.save_config()
        ml.subscribers.lock()
        ml.subscribers.add("USER1@example.com")
        ml.subscribers.add("user2@EXAMPLE.com")
        ml.subscribers.save()
        self.write_file_in_listdir(ml, "headers-to-add", "X-Foo: foo\n")
        self.write_file_in_listdir(ml, "headers-to-remove", "Received\n")
        self.sent_mail = []

    def tearDown(self):
        shutil.rmtree(DOTDIR)

    def write_file_in_listdir(self, ml, basename, contents):
        f = open(os.path.join(ml.dirname, basename), "w")
        f.write(contents)
        f.close()

    def configure_list(self, subscription, posting):
        list = self.mlm.open_list("foo@example.com")
        list.cp.set("list", "subscription", subscription)
        list.cp.set("list", "posting", posting)
        list.save_config()

    def environ(self, sender, recipient):
        eoc.set_environ({
            "SENDER": sender,
            "RECIPIENT": recipient,
        })

    def catch_sendmail(self, sender, recipients, text):
        self.sent_mail.append({
            "sender": sender,
            "recipients": recipients,
            "text": text,
        })

    def send(self, sender, recipient, text="", force_moderation=0, 
             force_posting=0):
        self.environ(sender, recipient)
        dict = self.mlm.parse_recipient_address(recipient, None, None)
        dict["force-moderation"] = force_moderation
        dict["force-posting"] = force_posting
        self.ml = self.mlm.open_list(dict["name"])
        if "\n\n" not in text:
            text = "\n\n" + text
        text = "Received: foobar\n" + text
        self.ml.read_stdin = lambda t=text: t
        self.mlm.send_mail = self.catch_sendmail
        self.sent_mail = []
        self.ml.obey(dict)

    def sender_matches(self, mail, sender):
        pat = "(?P<address>" + sender + ")"
        m = re.match(pat, mail["sender"], re.I)
        if m:
            return m.group("address")
        else:
            return None
        
    def replyto_matches(self, mail, replyto):
        pat = "(.|\n)*(?P<address>" + replyto + ")"
        m = re.match(pat, mail["text"], re.I)
        if m:
            return m.group("address")
        else:
            return None

    def receiver_matches(self, mail, recipient):
        return map(string.lower, mail["recipients"]) == [recipient.lower()]

    def body_matches(self, mail, body):
        if body:
            pat = re.compile("(.|\n)*" + body + "(.|\n)*")
            m = re.match(pat, mail["text"])
            return m
        else:
            return 1

    def headers_match(self, mail, header):
        if header:
            pat = re.compile("(.|\n)*" + header + "(.|\n)*", re.I)
            m = re.match(pat, mail["text"])
            return m
        else:
            return 1

    def match(self, sender, replyto, receiver, body=None, header=None,
              anti_header=None):
        ret = None
        for mail in self.sent_mail:
            if replyto is None:
                m1 = self.sender_matches(mail, sender)
                m3 = self.receiver_matches(mail, receiver)
                m4 = self.body_matches(mail, body)
                m5 = self.headers_match(mail, header)
                m6 = self.headers_match(mail, anti_header)
                no_anti_header = anti_header == None or m6 == None
                if m1 != None and m3 and m4 and m5 and no_anti_header:
                    ret = m1
                    self.sent_mail.remove(mail)
                    break
            else:
                m1 = self.sender_matches(mail, sender)
                m2 = self.replyto_matches(mail, replyto)
                m3 = self.receiver_matches(mail, receiver)
                m4 = self.body_matches(mail, body)
                m5 = self.headers_match(mail, header)
                m6 = self.headers_match(mail, anti_header)
                no_anti_header = anti_header == None or m6 == None
                if m1 != None and m2 != None and m3 and m4 and m5 and \
                   no_anti_header:
                    ret = m2
                    self.sent_mail.remove(mail)
                    break
        self.failUnless(ret != None)
        return ret

    def no_more_mail(self):
        self.failUnlessEqual(self.sent_mail, [])


class SimpleCommandAddressTestCases(IncomingBase):

    def testHelp(self):
        self.send("outsider@example.com", "foo-help@example.com")
        self.match("foo-ignore@example.com", None, "outsider@example.com", 
                   "Subject: Help for")
        self.no_more_mail()

    def testOwner(self):
        self.send("outsider@example.com", "foo-owner@example.com", "abcde")
        self.match("outsider@example.com", None, "listmaster@example.com",
                   "abcde")
        self.no_more_mail()

    def testIgnore(self):
        self.send("outsider@example.com", "foo-ignore@example.com", "abcde")
        self.no_more_mail()

class OwnerCommandTestCases(IncomingBase):

    def testList(self):
        self.send("listmaster@example.com", "foo-list@example.com")
        self.match("foo-ignore@example.com", None, "listmaster@example.com",
                   "[uU][sS][eE][rR][12]@" +
                        "[eE][xX][aA][mM][pP][lL][eE]\\.[cC][oO][mM]\n" +
                   "[uU][sS][eE][rR][12]@" +
                        "[eE][xX][aA][mM][pP][lL][eE]\\.[cC][oO][mM]\n")
        self.no_more_mail()

    def testListDenied(self):
        self.send("outsider@example.com", "foo-list@example.com")
        self.match("foo-ignore@example.com", None, "outsider@example.com", 
                   "Subject: Subscriber list denied")
        self.no_more_mail()

    def testSetlist(self):
        self.send("listmaster@example.com", "foo-setlist@example.com",
                  "From: foo\n\nnew1@example.com\nuser1@example.com\n")
        a = self.match("foo-ignore@example.com", 
                       "foo-setlistyes-[^@]*@example.com", 
                       "listmaster@example.com", 
                       "Subject: Please moderate subscriber list")
        self.no_more_mail()
        
        self.send("listmaster@example.com", a)
        self.match("foo-ignore@example.com", None, "listmaster@example.com",
                   "Subject: Subscriber list has been changed")
        self.match("foo-ignore@example.com", None, "new1@example.com",
                   "Subject: Welcome to")
        self.match("foo-ignore@example.com", None, "user2@EXAMPLE.com",
                   "Subject: Goodbye from")
        self.no_more_mail()

    def testSetlistSilently(self):
        self.send("listmaster@example.com", "foo-setlistsilently@example.com",
                  "From: foo\n\nnew1@example.com\nuser1@example.com\n")
        a = self.match("foo-ignore@example.com", 
                       "foo-setlistsilentyes-[^@]*@example.com", 
                       "listmaster@example.com", 
                       "Subject: Please moderate subscriber list")
        self.no_more_mail()
        
        self.send("listmaster@example.com", a)
        self.match("foo-ignore@example.com", None, "listmaster@example.com",
                   "Subject: Subscriber list has been changed")
        self.no_more_mail()

    def testSetlistDenied(self):
        self.send("outsider@example.com", "foo-setlist@example.com",
                  "From: foo\n\nnew1@example.com\nnew2@example.com\n")
        self.match("foo-ignore@example.com", 
                   None,
                   "outsider@example.com", 
                   "Subject: You can't set the subscriber list")
        self.no_more_mail()

    def testSetlistBadlist(self):
        self.send("listmaster@example.com", "foo-setlist@example.com",
                  "From: foo\n\nBlah blah blah.\n")
        self.match("foo-ignore@example.com", 
                   None,
                   "listmaster@example.com", 
                   "Subject: Bad address list")
        self.no_more_mail()

    def testOwnerSubscribesSomeoneElse(self):
        # Send subscription request. List sends confirmation request.
        self.send("listmaster@example.com",
                  "foo-subscribe-outsider=example.com@example.com")
        a = self.match("foo-ignore@example.com", 
                       "foo-subyes-[^@]*@example.com", 
                       "listmaster@example.com",
                       "Please confirm subscription")
        self.no_more_mail()
        
        # Confirm sub. req. List sends welcome.
        self.send("listmaster@example.com", a)
        self.match("foo-ignore@example.com", 
                   None, 
                   "outsider@example.com", 
                   "Welcome to the")
        self.no_more_mail()

    def testOwnerUnubscribesSomeoneElse(self):
        # Send unsubscription request. List sends confirmation request.
        self.send("listmaster@example.com",
                  "foo-unsubscribe-outsider=example.com@example.com")
        a = self.match("foo-ignore@example.com", 
                       "foo-unsubyes-[^@]*@example.com", 
                       "listmaster@example.com",
                       "Subject: Please confirm UNsubscription")
        self.no_more_mail()
        
        # Confirm sub. req. List sends welcome.
        self.send("listmaster@example.com", a)
        self.match("foo-ignore@example.com", None, "outsider@example.com", 
                   "Goodbye")
        self.no_more_mail()

class SubscriptionTestCases(IncomingBase):

    def confirm(self, recipient):
        # List has sent confirmation request. Respond to it.
        a = self.match("foo-ignore@example.com", 
                       "foo-subyes-[^@]*@example.com", 
                       recipient,
                       "Please confirm subscription")
        self.no_more_mail()
        
        # Confirm sub. req. List response will be analyzed later.
        self.send("something.random@example.com", a)

    def got_welcome(self, recipient):
        self.match("foo-ignore@example.com", 
                   None, 
                   recipient, 
                   "Welcome to the")
        self.no_more_mail()

    def approve(self, user_recipient):
        self.match("foo-ignore@example.com", None, user_recipient)
        a = self.match("foo-ignore@example.com", 
                       "foo-subapprove-[^@]*@example.com",
                       "listmaster@example.com")
        self.send("listmaster@example.com", a)

    def reject(self, user_recipient):
        self.match("foo-ignore@example.com", None, user_recipient)
        a = self.match("foo-ignore@example.com", 
                       "foo-subreject-[^@]*@example.com",
                       "listmaster@example.com")
        self.send("listmaster@example.com", a)

    def testSubscribeToUnmoderatedWithoutAddressNotOnList(self):
        self.configure_list("free", "free")
        self.send("outsider@example.com", "foo-subscribe@example.com")
        self.confirm("outsider@example.com")
        self.got_welcome("outsider@example.com")

    def testSubscribeToUnmoderatedWithoutAddressAlreadyOnList(self):
        self.configure_list("free", "free")
        self.send("user1@example.com", "foo-subscribe@example.com")
        self.confirm("user1@example.com")
        self.got_welcome("user1@example.com")

    def testSubscribeToUnmoderatedWithAddressNotOnList(self):
        self.configure_list("free", "free")
        self.send("somebody.else@example.com", 
                  "foo-subscribe-outsider=example.com@example.com")
        self.confirm("outsider@example.com")
        self.got_welcome("outsider@example.com")

    def testSubscribeToUnmoderatedWithAddressAlreadyOnList(self):
        self.configure_list("free", "free")
        self.send("somebody.else@example.com", 
                  "foo-subscribe-user1=example.com@example.com")
        self.confirm("user1@example.com")
        self.got_welcome("user1@example.com")

    def testSubscribeToModeratedWithoutAddressNotOnListApproved(self):
        self.configure_list("moderated", "moderated")
        self.send("outsider@example.com", "foo-subscribe@example.com")
        self.confirm("outsider@example.com")
        self.approve("outsider@example.com")
        self.got_welcome("outsider@example.com")

    def testSubscribeToModeratedWithoutAddressNotOnListRejected(self):
        self.configure_list("moderated", "moderated")
        self.send("outsider@example.com", "foo-subscribe@example.com")
        self.confirm("outsider@example.com")
        self.reject("outsider@example.com")

    def testSubscribeToModeratedWithoutAddressAlreadyOnListApproved(self):
        self.configure_list("moderated", "moderated")
        self.send("user1@example.com", "foo-subscribe@example.com")
        self.confirm("user1@example.com")
        self.approve("user1@example.com")
        self.got_welcome("user1@example.com")

    def testSubscribeToModeratedWithoutAddressAlreadyOnListRejected(self):
        self.configure_list("moderated", "moderated")
        self.send("user1@example.com", "foo-subscribe@example.com")
        self.confirm("user1@example.com")
        self.reject("user1@example.com")

    def testSubscribeToModeratedWithAddressNotOnListApproved(self):
        self.configure_list("moderated", "moderated")
        self.send("somebody.else@example.com", 
                  "foo-subscribe-outsider=example.com@example.com")
        self.confirm("outsider@example.com")
        self.approve("outsider@example.com")
        self.got_welcome("outsider@example.com")

    def testSubscribeToModeratedWithAddressNotOnListRejected(self):
        self.configure_list("moderated", "moderated")
        self.send("somebody.else@example.com", 
                  "foo-subscribe-outsider=example.com@example.com")
        self.confirm("outsider@example.com")
        self.reject("outsider@example.com")

    def testSubscribeToModeratedWithAddressAlreadyOnListApproved(self):
        self.configure_list("moderated", "moderated")
        self.send("somebody.else@example.com", 
                  "foo-subscribe-user1=example.com@example.com")
        self.confirm("user1@example.com")
        self.approve("user1@example.com")
        self.got_welcome("user1@example.com")

    def testSubscribeToModeratedWithAddressAlreadyOnListRejected(self):
        self.configure_list("moderated", "moderated")
        self.send("somebody.else@example.com", 
                  "foo-subscribe-user1=example.com@example.com")
        self.confirm("user1@example.com")
        self.reject("user1@example.com")

class UnsubscriptionTestCases(IncomingBase):

    def confirm(self, recipient):
        # List has sent confirmation request. Respond to it.
        a = self.match("foo-ignore@example.com", 
                       "foo-unsubyes-[^@]*@example.com", 
                       recipient,
                       "Please confirm UNsubscription")
        self.no_more_mail()
        
        # Confirm sub. req. List response will be analyzed later.
        self.send("something.random@example.com", a)

    def got_goodbye(self, recipient):
        self.match("foo-ignore@example.com", 
                   None, 
                   recipient, 
                   "Goodbye from")
        self.no_more_mail()

    def testUnsubscribeWithoutAddressNotOnList(self):
        self.send("outsider@example.com", "foo-unsubscribe@example.com")
        self.confirm("outsider@example.com")
        self.got_goodbye("outsider@example.com")

    def testUnsubscribeWithoutAddressOnList(self):
        self.send("user1@example.com", "foo-unsubscribe@example.com")
        self.confirm("user1@example.com")
        self.got_goodbye("user1@example.com")

    def testUnsubscribeWithAddressNotOnList(self):
        self.send("somebody.else@example.com", 
                  "foo-unsubscribe-outsider=example.com@example.com")
        self.confirm("outsider@example.com")
        self.got_goodbye("outsider@example.com")

    def testUnsubscribeWithAddressOnList(self):
        self.send("somebody.else@example.com", 
                  "foo-unsubscribe-user1=example.com@example.com")
        self.confirm("user1@example.com")
        self.got_goodbye("user1@example.com")

class PostTestCases(IncomingBase):

    msg = u"Subject: something \u00c4\n\nhello, world\n".encode("utf8")

    def approve(self, user_recipient):
        self.match("foo-ignore@example.com", None, user_recipient)
        a = self.match("foo-ignore@example.com", 
                       "foo-approve-[^@]*@example.com",
                       "listmaster@example.com")
        self.send("listmaster@example.com", a)

    def reject(self, user_recipient):
        self.match("foo-ignore@example.com", None, user_recipient)
        a = self.match("foo-ignore@example.com", 
                       "foo-reject-[^@]*@example.com",
                       "listmaster@example.com")
        self.send("listmaster@example.com", a)

    def check_headers_are_encoded(self):
        ok_chars = "\t\r\n"
        for code in range(32, 127):
            ok_chars = ok_chars + chr(code)
        for mail in self.sent_mail:
            text = mail["text"]
            self.failUnless("\n\n" in text)
            headers = text.split("\n\n")[0]
            for c in headers:
                if c not in ok_chars: print headers
                self.failUnless(c in ok_chars)

    def check_mail_to_list(self):
        self.check_headers_are_encoded()
        self.match("foo-bounce-.*@example.com", None, "USER1@example.com",
                   body="hello, world",
                   header="X-Foo: FOO",
                   anti_header="Received:")
        self.match("foo-bounce-.*@example.com", None, "user2@EXAMPLE.com",
                   body="hello, world",
                   header="x-foo: foo",
                   anti_header="Received:")
        self.no_more_mail()

    def check_that_moderation_box_is_empty(self):
        ml = self.mlm.open_list("foo@example.com")
        self.failUnlessEqual(os.listdir(ml.moderation_box.boxdir), [])

    def testSubscriberPostsToUnmoderated(self):
        self.configure_list("free", "free")
        self.send("user1@example.com", "foo@example.com", 
                  self.msg)
        self.check_mail_to_list()

    def testOutsiderPostsToUnmoderated(self):
        self.configure_list("free", "free")
        self.send("outsider@example.com", "foo@example.com", self.msg)
        self.check_mail_to_list()

    def testSubscriberPostToAutomoderated(self):
        self.configure_list("free", "auto")
        self.check_that_moderation_box_is_empty()
        self.send("user1@example.com", "foo@example.com", self.msg)
        self.check_mail_to_list()
        self.check_that_moderation_box_is_empty()

    def testOutsiderPostsToAutomoderatedRejected(self):
        self.configure_list("free", "auto")
        self.check_that_moderation_box_is_empty()
        self.send("outsider@example.com", "foo@example.com", self.msg)
        self.reject("outsider@example.com")
        self.check_that_moderation_box_is_empty()

    def testOutsiderPostsToAutomoderatedApproved(self):
        self.configure_list("free", "auto")
        self.check_that_moderation_box_is_empty()
        self.send("outsider@example.com", "foo@example.com", self.msg)
        self.approve("outsider@example.com")
        self.check_mail_to_list()
        self.check_that_moderation_box_is_empty()

    def testSubscriberPostsToModeratedRejected(self):
        self.configure_list("free", "moderated")
        self.check_that_moderation_box_is_empty()
        self.send("user1@example.com", "foo@example.com", self.msg)
        self.reject("user1@example.com")
        self.check_that_moderation_box_is_empty()

    def testOutsiderPostsToMderatedApproved(self):
        self.configure_list("free", "moderated")
        self.check_that_moderation_box_is_empty()
        self.send("outsider@example.com", "foo@example.com", self.msg)
        self.approve("outsider@example.com")
        self.check_mail_to_list()
        self.check_that_moderation_box_is_empty()

    def testSubscriberPostsWithRequestToBeModerated(self):
        self.configure_list("free", "free")

        self.check_that_moderation_box_is_empty()
        self.send("user1@example.com", "foo@example.com", self.msg,
                  force_moderation=1)
        self.match("foo-ignore@example.com", 
                   None, 
                   "user1@example.com", 
                   "Subject: Please wait")
        a = self.match("foo-ignore@example.com", 
                       "foo-approve-[^@]*@example.com", 
                       "listmaster@example.com")
        self.no_more_mail()

        self.send("listmaster@example.com", a)
        self.check_mail_to_list()
        self.check_that_moderation_box_is_empty()

    def testSubscriberPostsWithModerationOverride(self):
        self.configure_list("moderated", "moderated")
        self.send("user1@example.com", "foo@example.com", self.msg,
                  force_posting=1)
        self.check_mail_to_list()
        self.check_that_moderation_box_is_empty()

class BounceTestCases(IncomingBase):

    def check_subscriber_status(self, must_be):
        ml = self.mlm.open_list("foo@example.com")
        for id in ml.subscribers.groups():
            self.failUnlessEqual(ml.subscribers.get(id, "status"), must_be)

    def bounce_sent_mail(self):
        for m in self.sent_mail[:]:
            self.send("something@example.com", m["sender"], "eek")
            self.failUnlessEqual(len(self.sent_mail), 0)

    def send_mail_to_list_then_bounce_everything(self):
        self.send("user@example.com", "foo@example.com", "hello")
        for m in self.sent_mail[:]:
            self.send("foo@example.com", m["sender"], "eek")
            self.failUnlessEqual(len(self.sent_mail), 0)

    def testBounceOnceThenRecover(self):
        self.check_subscriber_status("ok")
        self.send_mail_to_list_then_bounce_everything()

        self.check_subscriber_status("bounced")
        
        ml = self.mlm.open_list("foo@example.com")
        for id in ml.subscribers.groups():
            bounce_id = ml.subscribers.get(id, "bounce-id")
            self.failUnless(bounce_id)
            self.failUnless(ml.bounce_box.has(bounce_id))

        bounce_ids = []
        now = time.time()
        ml = self.mlm.open_list("foo@example.com")
        ml.subscribers.lock()
        for id in ml.subscribers.groups():
            timestamp = float(ml.subscribers.get(id, "timestamp-bounced"))
            self.failUnless(abs(timestamp - now) < 10.0)
            ml.subscribers.set(id, "timestamp-bounced", "69.0")
            bounce_ids.append(ml.subscribers.get(id, "bounce-id"))
        ml.subscribers.save()

        self.mlm.cleaning_woman(no_op)
        self.check_subscriber_status("probed")

        for bounce_id in bounce_ids:
            self.failUnless(ml.bounce_box.has(bounce_id))

        self.mlm.cleaning_woman(no_op)
        ml = self.mlm.open_list("foo@example.com")
        self.failUnlessEqual(len(ml.subscribers.groups()), 2)
        self.check_subscriber_status("ok")
        for bounce_id in bounce_ids:
            self.failUnless(not ml.bounce_box.has(bounce_id))

    def testBounceProbeAlso(self):
        self.check_subscriber_status("ok")
        self.send_mail_to_list_then_bounce_everything()
        self.check_subscriber_status("bounced")
        
        ml = self.mlm.open_list("foo@example.com")
        for id in ml.subscribers.groups():
            bounce_id = ml.subscribers.get(id, "bounce-id")
            self.failUnless(bounce_id)
            self.failUnless(ml.bounce_box.has(bounce_id))

        bounce_ids = []
        now = time.time()
        ml = self.mlm.open_list("foo@example.com")
        ml.subscribers.lock()
        for id in ml.subscribers.groups():
            timestamp = float(ml.subscribers.get(id, "timestamp-bounced"))
            self.failUnless(abs(timestamp - now) < 10.0)
            ml.subscribers.set(id, "timestamp-bounced", "69.0")
            bounce_ids.append(ml.subscribers.get(id, "bounce-id"))
        ml.subscribers.save()

        self.sent_mail = []
        self.mlm.cleaning_woman(self.catch_sendmail)
        self.check_subscriber_status("probed")
        for bounce_id in bounce_ids:
            self.failUnless(ml.bounce_box.has(bounce_id))
        self.bounce_sent_mail()
        self.check_subscriber_status("probebounced")

        self.mlm.cleaning_woman(no_op)
        ml = self.mlm.open_list("foo@example.com")
        self.failUnlessEqual(len(ml.subscribers.groups()), 0)
        for bounce_id in bounce_ids:
            self.failUnless(not ml.bounce_box.has(bounce_id))

    def testCleaningWomanJoinsAndBounceSplitsGroups(self):
        # Check that each group contains one address and set the creation
        # timestamp to an ancient time.
        ml = self.mlm.open_list("foo@example.com")
        bouncedir = os.path.join(ml.dirname, "bounce-box")
        ml.subscribers.lock()
        for id in ml.subscribers.groups():
            addrs = ml.subscribers.in_group(id)
            self.failUnlessEqual(len(addrs), 1)
            bounce_id = ml.subscribers.get(id, "bounce-id")
            self.failUnlessEqual(bounce_id, "..notexist..")
            bounce_id = "bounce-" + id
            ml.subscribers.set(id, "bounce-id", bounce_id)
            bounce_path = os.path.join(bouncedir, bounce_id)
            self.failUnless(not os.path.isfile(bounce_path))
            f = open(bounce_path, "w")
            f.close()
            f = open(bounce_path + ".address", "w")
            f.close()
            self.failUnless(os.path.isfile(bounce_path))
            ml.subscribers.set(id, "timestamp-created", "1")
        ml.subscribers.save()

        # Check that --cleaning-woman joins the two groups into one.
        self.failUnlessEqual(len(ml.subscribers.groups()), 2)
        self.mlm.cleaning_woman(no_op)
        ml = self.mlm.open_list("foo@example.com")
        self.failUnlessEqual(len(ml.subscribers.groups()), 1)
        self.failUnlessEqual(os.listdir(bouncedir), [])
        
        # Check that a bounce splits the single group.
        self.send_mail_to_list_then_bounce_everything()
        ml = self.mlm.open_list("foo@example.com")
        self.failUnlessEqual(len(ml.subscribers.groups()), 2)
        
        # Check that a --cleaning-woman immediately after doesn't join.
        # (The groups are new, thus shouldn't be joined for a week.)
        self.failUnlessEqual(len(ml.subscribers.groups()), 2)
        self.mlm.cleaning_woman(no_op)
        ml = self.mlm.open_list("foo@example.com")
        self.failUnlessEqual(len(ml.subscribers.groups()), 2)
