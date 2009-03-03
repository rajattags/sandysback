import unittest


from sandy2.common.di import Injector
from sandy2.transports.mailer import MailParser, MailSender, MailListener

class MailTest(unittest.TestCase):
    
    def setUp(self):
        self.parser = MailParser()
        di = Injector(my_email_address = 'zander.alpha@gmail.com', my_email_name = 'Zander the Wonder Horse')
        di.configure(self.parser)
        pass
    
    def testParsing(self):
        message = self.parser.parse_raw_mail(self.message())
        self.assertNotEquals(message, None)
        
    def testMetadata(self):
        message = self.parser.parse_raw_mail(self.message())
        print self.parser.find_metadata(message)
        
        message = self.parser.parse_raw_mail(self.message_multi_part())
        print self.parser.find_metadata(message)
        
        message = self.parser.parse_raw_mail(self.reply())
        print self.parser.find_metadata(message)

    def testOutput(self):
        message = self.parser.parse_raw_mail(self.message())
        metadata = self.parser.find_metadata(message)
        metadata['reminder_message'] = "It's time to get up"
        reply = self.parser.construct_email(metadata, 'reminder_message')

        print str(reply)

    def xtestSend(self):
        message = self.parser.parse_raw_mail(self.message())
        metadata = self.parser.find_metadata(message)
        metadata['reminder_message'] = "It's time to get up"
        reply = self.parser.construct_email(metadata, 'reminder_message')
        
        server = MailSender(username='zander.alpha@gmail.com', password='PASSWORD_THAT_ISNT_THIS')
        server.send(reply)
        server.disconnect()

    def xtestFetch(self):
        server = MailListener(username='zander.alpha@gmail.com', password='PASSWORD_THAT_ISNT_THIS')
        server.run()

    def reply(self):
        return """                                                                                                                                                                                                                                                               
MIME-Version: 1.0
Received: by 10.181.56.6 with HTTP; Sun, 8 Feb 2009 15:16:29 -0800 (PST)
In-Reply-To: <176b2d550902081513j7a7e5ad7hc82e3cd94a830bae@mail.gmail.com>
References: <176b2d550902081513j7a7e5ad7hc82e3cd94a830bae@mail.gmail.com>
Date: Sun, 8 Feb 2009 23:16:29 +0000
Delivered-To: jameshugman@gmail.com
Message-ID: <176b2d550902081516p59c83e79pc2eb2af892624f7@mail.gmail.com>
Subject: Re: Reminder request
From: James Hugman <jameshugman@gmail.com>
To: jameshugman@gmail.com
Content-Type: multipart/alternative; boundary=0016e6dd8c4ca6131f04627071fc

--0016e6dd8c4ca6131f04627071fc
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

Reminder request received:

   - "Remind me in 20 minutes to go to bed"

This will be sent at *23:25*, today.

On Sun, Feb 8, 2009 at 11:13 PM, James Hugman <james@hugman.tv> wrote:
> Remind me in 20 minutes to go to bed.
>

--0016e6dd8c4ca6131f04627071fc
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

Reminder request received:<br><div style="margin-left: 40px;"><ul><li>&quot;<span style="background-color: rgb(255, 255, 51);">Remind me in 20 minutes to go to bed</span>&quot;</li></ul></div>This will be sent at <b>23:25</b>, today.<br>
<br>On Sun, Feb 8, 2009 at 11:13 PM, James Hugman &lt;<a href="mailto:james@hugman.tv">james@hugman.tv</a>&gt; wrote:<br>&gt; Remind me in 20 minutes to go to bed.<br>&gt;<br><br>

--0016e6dd8c4ca6131f04627071fc--                                                                                                                                                                                                                                                           
"""
    
    def message(self):
        return """                                                                                                                                                                                                                                                               
Delivered-To: zander.alpha@gmail.com
Received: by 10.140.208.13 with SMTP id f13cs1817rvg;
        Wed, 11 Feb 2009 13:11:53 -0800 (PST)
MIME-Version: 1.0
Received: by 10.181.234.13 with SMTP id l13mr22501bkr.123.1234386712255; Wed, 
    11 Feb 2009 13:11:52 -0800 (PST)
Date: Wed, 11 Feb 2009 21:11:52 +0000
Message-ID: <176b2d550902111311j48c97a02pa1ed7d921fe06465@mail.gmail.com>
Subject: Another tester
From: James Hugman <jameshugman@gmail.com>
To: zander.alpha@gmail.com
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

Remind me when it's time to stop.
"""
    
    def message_multi_part(self):
        return """From James.Hugman@lhasalimited.org Thu Feb 12 02:10:23 2009
Delivered-To: zander.alpha@gmail.com
Received: by 10.140.208.13 with SMTP id f13cs2379rvg; Thu, 12 Feb 2009
 02:10:23 -0800 (PST)
Received: by 10.86.59.2 with SMTP id h2mr1311753fga.30.1234433421119; Thu,
 12 Feb 2009 02:10:21 -0800 (PST)
Return-Path: <James.Hugman@lhasalimited.org>
Received: from mail181.messagelabs.com (mail181.messagelabs.com
 [85.158.139.67]) by mx.google.com with SMTP id
 12si1394563fgg.53.2009.02.12.02.10.20; Thu, 12 Feb 2009 02:10:21 -0800 (PST)
Received-SPF: neutral (google.com: 85.158.139.67 is neither permitted nor
 denied by best guess record for domain of James.Hugman@lhasalimited.org)
 client-ip=85.158.139.67;
Authentication-Results: mx.google.com; spf=neutral (google.com:
 85.158.139.67 is neither permitted nor denied by best guess record for
 domain of James.Hugman@lhasalimited.org)
 smtp.mail=James.Hugman@lhasalimited.org
X-VirusChecked: Checked
X-Env-Sender: James.Hugman@lhasalimited.org
X-Msg-Ref: server-3.tower-181.messagelabs.com!1234433418!15558357!1
X-StarScan-Version: 6.0.0; banners=-,-,-
X-Originating-IP: [82.71.235.104]
Received: (qmail 15463 invoked from network); 12 Feb 2009 10:10:18 -0000
Received: from unknown (HELO lukpc95.lhasalimited.org) (82.71.235.104) by
 server-3.tower-181.messagelabs.com with SMTP; 12 Feb 2009 10:10:18 -0000
Content-Transfer-Encoding: 7bit
X-MimeOLE: Produced By Microsoft MimeOLE V6.00.3790.4325
Importance: normal
Priority: normal
Content-Class: urn:content-classes:message
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="----_=_NextPart_001_01C98CFA.16D83FBD"
Subject: A Test from Outlook!
Date: Thu, 12 Feb 2009 10:10:10 -0000
Message-ID: <23DE7AACEDEEFB44BAE3C794CA2F4A69035757@lukpc95.lhasalimited.org>
X-MS-Has-Attach: 
X-MS-TNEF-Correlator: 
Thread-Topic: A Test from Outlook!
thread-index: AcmM+gfvDHYS03EFQgmYbnaYSl67Tw==
From: "James Hugman" <James.Hugman@lhasalimited.org>
To: <zander.alpha@googlemail.com>
X-Evolution-Source: imap://zander.alpha@imap.gmail.com/


------_=_NextPart_001_01C98CFA.16D83FBD
Content-Type: text/plain; charset="US-ASCII"
Content-Transfer-Encoding: 8bit

 

 

-- 

James Hugman

Software Development

Extension: 6076

 

 

 


--------------------------------------------------------------------------
http://www.lhasalimited.org/index.php?cat=183&amp;owner=5&amp;sub_cat=183
http://campaigns.valtira.com/LhasaLimitedEmailSigEvents
http://www.lhasalimited.org/newsletter
_________________________________________________
Switchboard: +44 (0)113 394 6020
Customer Support: +44 (0)113 394 6030
Sales: +44 (0)113 394 6060
_________________________________________________
Lhasa Limited, a not-for-profit organisation, promotes scientific knowledge & understanding through the development of computer-aided reasoning & information systems in chemistry & the life sciences. Registered Charity Number 290866.
This communication, including any associated attachments, is intended for the use of the addressee only and may contain confidential, privileged or copyright material. If you are not the intended recipient, you must not copy this message or attachment or disclose the contents to any other person. If you have received this transmission in error, please notify the sender immediately and delete the message and any attachment from your system. Except where specifically stated, any views expressed in this message are those of the individual sender and do not represent the views of Lhasa Limited. Lhasa Limited cannot accept liability for any statements made which are the sender's own. Lhasa Limited does not guarantee that electronic communications, including any attachments, are free of viruses. Virus scanning is recommended and is the responsibility of the recipient.

------_=_NextPart_001_01C98CFA.16D83FBD
Content-Type: text/html; charset="US-ASCII"
Content-Transfer-Encoding: 8bit

<html><head><META content="text/html; charset=us-ascii" http-equiv="Content-Type">

<STYLE><!-- /* Style Definitions */ p.1f8c4b90-3305-4283-aeb4-6f2ad1299794, li.1f8c4b90-3305-4283-aeb4-6f2ad1299794, div.1f8c4b90-3305-4283-aeb4-6f2ad1299794, table.1f8c4b90-3305-4283-aeb4-6f2ad1299794Table    {margin:0cm; margin-bottom:.0001pt;}div.Section1 {page:Section1;}--></STYLE>

<META CONTENT="text/html; charset=us-ascii" HTTP-EQUIV="Content-Type">
<meta content="Microsoft Word 11 (filtered medium)" name=Generator>
<style>
<!--
 /* Style Definitions */
 p.MsoNormal, li.MsoNormal, div.MsoNormal
    {margin:0cm;
    margin-bottom:.0001pt;
    font-size:12.0pt;
    font-family:"Times New Roman";}
a:link, span.MsoHyperlink
    {color:blue;
    text-decoration:underline;}
a:visited, span.MsoHyperlinkFollowed
    {color:purple;
    text-decoration:underline;}
span.EmailStyle17
    {mso-style-type:personal-compose;
    font-family:Arial;
    color:windowtext;}
@page Section1
    {size:612.0pt 792.0pt;
    margin:72.0pt 90.0pt 72.0pt 90.0pt;}
div.Section1
    {page:Section1;}
-->
</style>

</head><BODY><SPAN STYLE="COLOR: #000255">
<P>

<div class=Section1>

<p class=MsoNormal><font face=Arial size=2><span style='font-size:10.0pt;
font-family:Arial'><o:p>&nbsp;</o:p></span></font></p>

<p class=MsoNormal><font face=Arial size=2><span style='font-size:10.0pt;
font-family:Arial'><o:p>&nbsp;</o:p></span></font></p>

<p class=MsoNormal><font face=Arial size=2><span style='font-size:10.0pt;
font-family:Arial'>-- </span></font><o:p></o:p></p>

<p class=MsoNormal><font face=Arial size=2><span style='font-size:10.0pt;
font-family:Arial'>James Hugman</span></font><o:p></o:p></p>

<p class=MsoNormal><font face=Arial size=2><span style='font-size:10.0pt;
font-family:Arial'>Software Development</span></font><o:p></o:p></p>

<p class=MsoNormal><font face=Arial size=2><span style='font-size:10.0pt;
font-family:Arial'>Extension: 6076</span></font><o:p></o:p></p>

<p class=MsoNormal><font face="Times New Roman" size=3><span style='font-size:
12.0pt'>&nbsp;<o:p></o:p></span></font></p>

<p class=MsoNormal><font face="Times New Roman" size=3><span style='font-size:
12.0pt'>&nbsp;</span><o:p></o:p></font></p>

<p class=MsoNormal><font face="Times New Roman" size=3><span style='font-size:
12.0pt'><o:p>&nbsp;</o:p></span></font></p>

</div>

</P>
<P>
<HR>

<P><A HREF="http://www.lhasalimited.org/index.php?cat=183&owner=5&sub_cat=183">Book Software Training </A><BR><A HREF="http://campaigns.valtira.com/LhasaLimitedEmailSigEvents">Meet Lhasa Limited Sales Staff at Conferences</A><BR><A HREF="http://www.lhasalimited.org/newsletter">Check out our latest Informatica Newsletter</A></P>
<P>_________________________________________________</P>
<P><B>Switchboard: +44 (0)113 394 6020<BR>Customer Support: +44 (0)113 394 6030<BR>Sales: +44 (0)113 394 6060</B><BR>_________________________________________________ </P>
<P><SPAN STYLE="FONT-SIZE: 12px">Lhasa Limited, a not-for-profit organisation, promotes scientific knowledge&nbsp;& understanding through the development of computer-aided reasoning&nbsp;& information systems in chemistry&nbsp;& the life sciences. Registered Charity Number 290866.</SPAN></P><SPAN STYLE="FONT-SIZE: 10px">
<P>This communication, including any associated attachments, is intended for the use of the addressee only and may contain confidential, privileged or copyright material. If you are not the intended recipient, you must not copy this message or attachment or disclose the contents to any other person. If you have received this transmission in error, please notify the sender immediately and delete the message and any attachment from your system. Except where specifically stated, any views expressed in this message are those of the individual sender and do not represent the views of Lhasa Limited. Lhasa Limited cannot accept liability for any statements made which are the sender's own. Lhasa Limited does not guarantee that electronic communications, including any attachments, are free of viruses. Virus scanning is recommended and is the responsibility of the recipient.</P></SPAN>
<P></P>
<P></P>
<P></P></P></SPAN></BODY></html>
------_=_NextPart_001_01C98CFA.16D83FBD--"""

if __name__ == '__main__':
    unittest.main()
