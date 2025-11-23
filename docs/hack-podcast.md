9:46
Um so but as you've noticed uh this is very much you know uh from the title this is a grado agents and mcp
9:53
hackathon. Uh so what is gradio doing here? Um if you know gradio already you
9:58
might ask um isn't gradio a python library for building UIs you know user
10:03
interfaces applications demos uh what does it have to do with agents and mcps?
10:09
Uh in fact isn't just a python library for building UIs. Uh the way we think
10:15
about it actually is Graddio um lets you easily take any sort of machine learning
10:20
model um or collection of models or or kind of generally any piece of like any
10:26
any Python function really uh you know and that's very general of course and it
10:31
lets you expose it to the right kind of uh to to to different uh end users in
10:39
the right format right so it lets you build UIs for humans Um, but every gradu
10:45
application also comes with a pre-built API for software. It also comes um as as
10:52
I'll show in just a second, every Gradu application is also an MCP uh or can be deployed as an MCP very very easily,
10:59
making that same application something that can be consumed by an LLM. Um, so
11:04
that's all kind of abstract and hypothetical. Let me make it much more concrete.
11:10
So um let me make it much more concrete. So uh here what we have is we have a uh
11:18
we have a gradu application. Um we it's a function. I'm going to call it stylize image. And what that'll do is that'll
11:25
take a function uh that'll take in an image and a style and it'll return a mod
11:31
a modified style. Right? So you can imagine that as something like for example it takes in a input image which
11:37
could be a photo and it takes in a style which could be something like I don't know a studio giblly image style and
11:43
then it returns a stylized image which is a modified uh modified function and so what you can do is you can deploy
11:49
this function as a gradu application very easily by taking an inputs like an
11:55
image and a dropown and then the output is also an image. So you can see it deploys this as a UI very easily right
12:02
here. Um so you know this is something that's designed for humans but uh so it's something that's
12:09
designed for humans but you can also use this gradio application programmatically via an API. So this is something that
12:15
comes with every gradio application. You can also use the same application via UI
12:20
but what you can also do is you can pass in one extra parameter MCP server equals
12:25
true. And what that does is that let you can see it changed here use via API or
12:30
MCP. And what that does it lets LLMs actually use this gradio application uh
12:36
you know directly via uh well at the end of the day a human using that LLM can
12:41
now use your gradio application via natural language. Um and then once you have your gradu
12:48
application you can actually deploy these gradu applications as MCP servers on the hub right so on the hugging face
12:55
hub on spaces so if you've used if you've deployed gradu applications on spaces before you know it's kind it's a
13:00
free hosting platform for gradu applications um you can deploy your code exactly as is and then you can select
13:07
what kind of hardware you want if you want if it runs on CPU then it's free if it runs on GPU there's different options
13:13
but what you can also do is you actually deploy your MCP servers on on spaces as well. So what this does is uh on spaces
13:21
you can actually now filter by MCP compatible gradio spaces. So you can find a bunch of of of you know MCP
13:28
servers that you can use within your LLMs. So once you open it up now you can use that gradio application or that tool
13:35
with any LLM. So here for example I'm using this within cursor but you could use it within cloud or um anything else
13:41
really. Um, and one thing I'll just share, uh,
13:48
this is very new. We haven't we haven't shared this publicly yet, but this radio MCP integration, it supports not just
13:54
SSC and SD, uh, the standard IO, uh, protocols, but it also actually as of a
14:00
few days ago, supports the streamable HTTP protocol as well. And now this is uh great because this basically means no
14:06
matter what your LM you know client uses whether it's any of these protocols um
14:12
you can actually you know use uh build a gradu application and make it work with your client. Um okay um and that is just
14:20
a taste of what you can do in this hackathon. You can there's a lot more um that you can do. You don't have to just
14:25
build MCP servers. You don't have to just build agents. Um we'll talk about the different tracks. Uh I'll hand it
14:31
over to Yuvie just shortly uh for that. But there's a lot more that you can do.
14:36
Um and uh this actually this uh poster here is actually outdated now because we have uh you know we have more prizes
14:43
than that. We have a lot of cash and credit uh that's going to be awarded to all of the all of the registrants but
14:48
then of course all the winners as well. Um so with that we hope u yeah and all you need basically for any of this um is
14:55
you know all of these resources are available online. And all you need really is a computer. You need a hugging
15:00
face account. Um which everyone probably if you if you've registered, you have a hugging face account. Um if you're
15:06
joining the live stream without registering, you will need to do that. Um we can share the registration link afterwards. Um and then if uh many of
15:13
our partners are providing API credits like I mentioned um and and um so you might need accounts with those folks as
15:20
well. Um and you know, we'll hear from a couple of them talking about how how that works. um if you're planning on
15:26
using those API credits. But with that um I want to actually transi uh hand this over to
15:32
Yuvie who's going to talk more about the hackathon details and resources. So more of the more the actual details. So let
15:38
me stop sharing my screen.
15:44
Let me go ahead and add your screen as well.
Hackathon details and resources
15:51
Hey everyone. Yeah, you can hear. Yeah, thanks uh
15:57
thanks for working uh for that uh wonderful presentation.
16:03
Um let me start my slides. Just one second. I hope you guys
16:08
can hear me well. All right.
16:17
So yeah just one second and I'll begin. So like Kubaka said uh I'll be telling
16:24
you about uh you know what this hackathon is about uh what resources you
16:29
have and what are the different tracks and how long it is and all those things. So yeah
16:36
um right so we have started yesterday and uh we will go until Sunday June 8th.
16:44
Uh you have this whole one week to build and uh you have to submit keep in mind that you have to submit your uh your
16:50
your entries uh by June 8th uh by UTC day end. uh this whole this whole thing
16:56
is online and um you can participate as an individual or as a team team uh you
17:01
can go up till uh you know five members and uh so we we never expected this that
17:08
we will blow up so much right now we are at uh 3,000 uh more than 3,000 participants and we are still
17:14
registering so knock yourself out uh if you haven't registered yet and we have
17:19
around uh 16 uh you know $16,000 uh in cash prizes and then more than 1 million
17:26
in uh API credits and computer credits from our generous sponsors. And then
17:32
uh there are three tracks. So the first track is uh is around MCP. Uh so what
17:39
what I mean by tracks is that you know you can uh submit uh for these three things like three three broad
17:46
categories. The first category is uh it should be an MCP related. So you can you
17:53
I think already covered that you can create any radio app as a as an MCP server. So you know uh you can do that
18:01
and um so the second track will be uh custom components and uh so custom
18:07
components is like uh you know if you are using uh radio you might have
18:13
questions like you know I wish if I can do something else using radio I can build something else I can if there
18:18
would have been a different component all those things. So you can you can create any component you want using
18:25
radio. So we want to see how you know what community builds with uh you know
18:30
with agentic uh you know UI in mind. If you have something like that in mind just go on. And then last thing is an
18:37
agentic demo and end to end agentic app using radio and you know using uh one of
18:42
the sponsors that we have like for example llama index or uh APIs from sova
18:48
or anthropic or openi or mistra so on and uh
18:56
so so yeah so we have for all these different tracks we have different prizes. So for every track we have two
19:03
prizes. First one is uh $2,500 and then second one is $500. Um the cash prizes are uh offered
19:12
by Having as well as some of our sponsors. So there is another prizes.
19:18
There are few special category prizes like for example we have llama index which is sponsoring $1,000 US. So if uh
19:26
so for example if you build an app which is using lava index and you know with MCP and its agent tech so you stand to
19:33
win that prize and uh similarly we have uh something like uh community choice.
19:39
So, so like for example, if you you have the highest amount of engagement on your app or you know you have the highest
19:47
number of likes then you stand to win and then there are other PL prizes uh
19:52
sponsored by u other you know uh sponsors like for example we have model which is sponsoring a $5,000 US it's
20:00
similar to lumber index you have to use model in this and you know you can mix these uh uh two things like for example
20:07
you can build uh build an app that uses model and that uses MR and that uses the
20:12
llama index as well and you can you know you can qualify for all these categories and I can imagine that you know you will
20:17
have uh uh questions more questions about these kind of uh awards and categories. So feel free to drop us any
20:23
u any of your questions or suggestions or you know ideas uh with us in discord.
20:28
So we are really open to listening to that. Um yeah so uh our sponsors have very
20:35
generously uh you know uh planned out these uh API credits. So every
20:41
participant gets uh model credit. So what you can use it uh for is you know you can use it for uh hosting inferences
20:47
for computer heavy models and for example flux or you know quen 3 or deep
20:54
carbon you can use model for that then you can use nas for API credits again uh
20:59
these are open source uh strong powerful lms that you can use for it then you have anthropic and openi which you can
21:05
use uh their uh APIs like cloud and gp40 and so on and then hang is providing uh
21:14
$25 worth of inference provider credits. Um, and we have Hyperbolic, we have
21:20
Mistral, and we have Zamano as well. So, so the timeline for this week is
21:26
like today we have this live kickoff. Then tomorrow what we're going to do is we have these office hours and in those
21:33
uh uh so we have these office hours planned throughout the week and during these office hours what you can do is you know you can ask uh you will be uh
21:41
you will be having these uh folks from different sponsors or different teams within uh
21:47
within like you can have uh you'll have a walker tomorrow uh answering your MCP related questions uh what you can build
21:53
with radio what is possible right now and then you'll have llama index as
21:59
later uh uh later tomorrow and then Mr. and then uh we have someone for coming
22:04
from 70 on June 5th and then again we have Freddy and Pete from in-house
22:10
talking about custom components on June 5th. So the idea basically is that you know we want to provide you ample
22:15
resources and you know guidance so that you can build great apps and you have fun you know while building all these
22:21
apps and you know you're not frustrated and you know we ask you're stuck with any technical questions other than these
22:27
office hours always uh we would encourage you to feel free uh in dropping any questions you have uh on
22:34
the discord channels on different discord channels that we have and uh yeah just feel free to engage with the
22:40
community or with us tag us any wonderful HF folk and we'll be very happy to help you out with that and then
22:47
next week on Friday most likely we will be announcing winners uh but if we get let's say around thousand applications
22:54
applications uh so we might you know we might have to defer it by a day or two but let's see what happens um so I think
23:03
also u covered this we have different resources we have uh different courses from wonderful folks at hugging face we
23:09
have MCP course we have agent course and then there are different guides from radio uh like around MCP around agents
23:17
uh around custom components and then apart from these uh we have uh resources which are pulled in from all these
23:22
bonuses uh they might be talking about that right now and uh I will also be
23:28
sending you emails and communications listing all those things that you have so that you know all these things are at your fingertips and you know you can
23:35
refer them anytime. Um so yeah like I said we have a live support going on on discord. Uh
23:43
we encourage everyone to you know follow community guidelines while asking questions and while helping others out.
23:50
Uh we are also sending uh regular communications about credits about you know other updates via emails and uh we
23:57
are making constant updates on our homepage and I believe you all have already joined the orc. uh and if not
24:03
you if you haven't joined it I'll suggest I'll request rather that you know join go ahead and join the orc
24:08
because the thing is if you are there in the organization then only you are eligible to submit your u entry for our
24:15
consideration uh so yeah please make a note of that and uh so what we have also come up with is that you know if we see
24:22
someone who is uh helping others out on discord we would be very happy to send
24:27
out hugging face swag on the way uh so yeah just just feel free um to help uh
24:34
you know help everyone out if you have some time on your hands. Um the guidelines are if you are
24:41
uh this is uh just an example how you can tag your space uh or hanging pace.
24:47
So for example, if you are if what you have built you think it covers two tracks. So what you can do is you know
24:53
you can tag you can add a tag metadata tag and these tags these specific tags
24:59
they are mentioned on the uh on the org page as well. So feel free to check that out and uh if you have if you think you
25:06
know if you're building with let's say for example something with cursor or client or somebody else somewhere else then please please include your video so
25:13
that we can verify it your recording of your app your demo and you know link to it upload it on YouTube or in any other
25:20
way if you want to share with us just link it to us in the space that you will create so even if you don't have
25:26
anything in in your space include a nice read me that you know that has everything what you have built
25:32
about if you are submitting as a team make sure that you know you are including everything uh about your team
25:37
members uh like especially the HF username I don't want you to list their email addresses but yeah please do
25:44
mention their their usernames um and then uh your next steps join the
25:50
org if you haven't complete the registration form we are open till June 8th and if you want to refer this this
25:59
hackathon to your friends or your colleague Just feel free to do that. We are in uh you know we are um accepting
26:06
applications. Pick your track and idea start building now because time is running out and jump into discord
26:13
anytime and feel free to tag us and uh that's it from me. Um yeah let's build I
26:20
think u I can hand it over to you worker if you if you're still around.
26:26
Yeah absolutely. Um I think great. Thanks Juvie. Uh let's uh bring in some folks uh who are generously bring uh
26:32
sponsoring the uh hackathon. Yeah. Uh all right. Should we start with Justin from Samova? Justin, are you ready?
26:40
All right. Can you guys can uh can you hear me? I just want to make sure that people Yes. And we can hear you. You can
Sponsor section - Sambanova
26:48
hear me fine. Okay, great. Well, my name is Justin. I'm from SANOVA. I'm gonna go really quickly over this. If you're
26:54
going to take a screenshot of the page of the of the live stream, this is the most important page here. So, we're
27:00
giving out a prize for the best use of the Samanova API. I'm also hosting office hours on June 5th at 10:00 a.m.
27:08
That's my email down there. I've got my Discord handle. I'm going to be on Discord the entire time. And if you sign
27:14
up using this link, so I would take a screenshot of this URL here and this QR code. If you sign up for this link,
27:20
we're going to give you $5 in free credits. and we'll tell you how we can use those credits to actually build an MCP server in a second. All right, so
27:28
let's just get going here. Um, so one thing about it, uh, we did give out $25
27:34
in free credits to the first 250 participants, but that URL will give you $5 of of credits and we're also giving
27:41
out $500 to the best use of the Sonova API. So let's dive deep into what Sonova
27:47
a API is. AI is. So, we're the most fastest and efficient AI accelerator
27:53
that serves open-source models on our cloud platform. So, when you go to that link that I just showed, I'm going to
27:59
show it to you at the end of this presentation. It would bring you to this dashboard here, and you can see these
28:05
are all the open-source models that we host right now, including DeepS, Llama
28:10
3.1, Llama 4, and even Whisper. All right. And within each of these models,
28:16
we do have a gradial code here to that you can access the models. We have Python code and of course a code request
28:22
that you can access using an OpenAI compatible uh URL. Okay. So I'm just
28:27
going to show you really quickly how you can go into like some a model that we have. This is our playground uh that you
28:33
can access. And if you want to see what I'm doing here, you can actually hit view code here and it'll show you
28:39
exactly how to get um the AI running, the large language model running using these endpoints. But I'm going to go
28:45
really quickly and just hit one of our sample um prompts here. And what you can
28:50
see is that we pride ourselves on being like the fastest LM. And you can see that we're getting it at 0.13 time the
28:57
first token and 221 tokens per second. So, if you're trying to build an agent that's super fast, super efficient, I
29:03
would recommend using Sabonova. So, I'm going to talk to you. I think right now what's really important is you want to
29:09
get building an MCP server. I would recommend using SANOVA with client. Why?
29:15
Because it's free. Because we give you $5 in credits and you can actually use that to build an MCP server really quickly. So, really quickly, the way I'm
29:22
going to demonstrate this is if I go to the Sonova cloud here and I type in Deepseek R1. If I type something like
29:28
build me an an MCP server right here. It's going to
29:34
be really fast in building me an MCP server, but it doesn't really know what's MCP server. And here I thought
29:39
that's a Minecraft server. What's really cool is that the Gradio uh docs actually
29:45
has an MCP server. And I hooked that up to client so that you can actually use
29:50
this Gradio server and client and the free credits to build an MCP server really quickly. So, I'm going to jump
29:56
right into it uh quickly since we're almost running out of time here. So, once you run up, build up, I'm going to
30:02
show you my screen. Uh sorry, I'm going to present to you uh about that. Give me
30:08
one second to uh present to you
30:15
my Okay, great. All right. So, now I've got
30:20
client up and running here. This is Visual Studio Code. Client is an extension. Again, if you go and sign up
30:26
using that URL I showed you, you can actually enable uh Sambbernova as one of the providers and $5 credit should be
30:33
more enough for you to build an MCP server using this client client bot extension and you would go ahead and
30:39
grab your API provider and Sabonova API key in the in the sandbox that I showed you. Once you can do that, go ahead and
30:46
uh configure the Gradio server that I showed you and I can show you share you those links later on. And these MCP
30:53
servers actually load up into the gradial docs, which is really cool because now client has a way to
30:58
understand how to build an MCP server. So I'm going to show you really quickly. I've already got a prompt that does
31:04
that. And just as you can see, the prompt says read the Gradio documentation and build an MCP server
31:09
for me. And then actually goes into the Gradio MCP server, reads the documentation, actually builds the MCP
31:15
server. So I'm actually going to do the task, but I'm not going to do the task right now. I'm going to encourage you to do that. uh and ping me if you have any
31:21
questions, but it actually can build an MCP server using the gradio documentation. So, now that I'm just
31:27
actually running out of time here, I'm going to flash the most important uh
31:32
slide I have here, which is we're giving $500 best use of Sonova API. If you want
31:37
to get $5 in free credits, go to this bit.ly link here. And just to recap,
31:42
what I showed you was to get $5 in free credit and surn over uh the API AI use
31:48
client to build your MCP server and then also use the grad docs mcb server within
31:54
client to understand how to build MCP server and then that's all I've got to share. Thank you. So I'm going to pass
32:00
it back to uh yeah. Yeah. Awesome. Thanks Justin. Very very cool. Very meta. I love it. Um I am we're going to
32:09
change uh shift gears a little bit. Uh Justin, thanks so much. I'm going to bring on Tuana uh if you're ready from
Sponsor section - LlamaIndex
32:15
Llama Index. Um all right, you should be live. Hey, can you hear me properly?
32:22
Yeah. All right, so um since we don't have a lot of time, I've decided to do a
32:27
very quick intro into what Llama Index and the Llama Cloud landscape looks like and what you can do with the Llama Index
32:34
tooling. Um, so what we provide is a event-driven agentic workflow, which
32:41
means that you can customize agentic workflows to your will basically. And these types of workflows, so what you're
32:47
seeing on this screen, the this funky looking graph is actually a pretty complex agentic workflow that is also
32:52
using graph rack under the hood. But each of these steps and events you can define completely yourself. So it's very
33:00
flexible in defining very custom agentic workflows. You can also build things
33:05
that can root root uh that run in parallel that have decision nodes etc as
33:11
well. But something that we recently added and we don't we haven't uh had a
33:17
lot of users just yet. This is super new. So I would love to see uh if you do want to create MCP servers based on
33:24
aentic workflows yourself, you can scan this QR code, but I'm sure we're going to send these resources out to you later
33:30
as well. Uh we've recently added a very neat helper function that allows you to
33:35
convert any agentic workflow into its own little MCP server. Uh the same way
33:41
you can also use pre-existing MCP servers as tools for your uh agentic
33:46
workflows in llama index. So you can actually I think there's a lot of things that you can build with llama index that would fit any of the three tracks that
33:53
uh we have going on right now. Lastly, I want to briefly talk about Llama Cloud
33:58
because everyone who signs up to Llama Cloud will get 10K credits. So, that's about 10 to$15 worth of credits, but it
34:05
means that you can use all of the Llama Cloud uh products that allows you to
34:12
store chunk pre-processed data. Um, one of the latest things we added is Llama
34:17
Extract, which is a great way to extract structured outputs out of complex document sources. Um, and then you can
34:24
also use llama par which allows you to bring in notoriously difficult to handle
34:30
file types and par them into a way that an LLM can make use of. And you get
34:36
access to all of these and you can also use them as an MCP server. And I have an
34:42
example um repository linked here for that as well. So anything that you build
34:47
in llama cloud whether it's something that pauses extracts stores you can um
34:52
wrap that wrap that up into an MCP server and provide that to any other agentic workflow or application as
34:59
well. And then the last thing I guess this is the main one that I should share is this is the llama cloud signup that
35:06
allows you to get 10k free credits um that allows you to use par extract and index as well. I'm going to be hosting a
35:15
uh Discord office hours. I believe it's Discord office hours and I think it's at 9:00 am PT, but I'll ask UV or Abu Bakr
35:22
to confirm that tomorrow with uh my colleague. Uh we'll be there to answer
35:28
any of your questions. Um we can even do screen shares and uh try out some code
35:33
together. Uh but that should be tomorrow at 9:00 a.m. PT hopefully. And with
35:39
that, I can hand over to the next speaker.
35:44
Thanks so much, Toana. Very, very cool. Um, uh, and with that, we're gonna have our final speaker, Joffrey from Mistral.
35:50
So, I'm gonna remove and then add Joffrey here. Hey Joffrey, should be
Sponsor section - Mistral AI
35:57
live. Hey, can you hear me? Yep. All good. So, hi everyone and welcome. I'm
36:03
Joffrey, a developer relation engineer from Mistro, but some of you might recognize me from the agent course that
36:09
I led while um I was doing my time at Hugging Face. So, I'm here to showcase
36:15
the potential of ML offering in the context of this hackathon. Um first, let's talk about
36:21
what we provide during this hackathon. We are providing $25 of credits for you to build with Mistl. If you end up
36:28
winning the Mistral Choice Award, we will grant you an additional $2,000 of credit to push your ID. Finally, I will
36:36
also be present in the Discord to answer potential question you may have. Two um 2025 was very packed for
36:45
Mistrol um as a number of release, but let me quickly highlight three of them that might be amazing for you uh during
36:52
this hackathon. Uh we have Destro an open source model specialized in software engineering task. Um and our
36:59
OCR API that would be great candidates if you want to build MCP servers around them. And last but not least, we just
37:08
released last week our agent API which allow you to create agents and um
37:13
interact with them really easily. Let's spend a little bit more time on that. So
37:18
the agent API is directly integrated into our client. So it's really easy to
37:24
in to start building with it. You don't need to install new Excel library. You
37:29
can just upgrade your Python version of the client and and start and you're good
37:34
to go. So uh agent API and all the conversations the agent and a different
37:40
set of tools. Let's spend a little bit time on this set of tools that you can
37:45
that you can build with. So there are actually three different types. Uh the
37:51
first one are the connectors. Those are built-in uh tools that are in the PI
37:56
that you don't have to code yourself. So you have a web search, a code interpreter, an immer generator and a
38:01
document library. Um those are built in. You can think of them as um some kind of
38:07
MCP server that we build on our side. Uh so that you don't have to code those
38:13
very generic and complex function otherwise um complex optimized function.
38:19
So of course you can still use traditional function calls um in the traditional fashion function that are
38:26
local and uh that you call locally and the one that you're most interested about um most likely are the MCP server
38:34
are agent APIs MCP compatible. Uh so
38:40
little reminder but MCP is a standard that provide you with a set of tools in the format of an API. Uh if you build
38:48
MCPS with gradio um it's actually super easy to use um from hugging face uh and
38:56
through our agent API because all spaces from hugging face have a public URL and you can just find that public URL into
39:05
um your your space instantiate an SSC server from that URL uh into our client
39:12
and just start uh talking with your your agent. The code sample here is not fully
39:19
complete for lack of space. So you can find the collab um directly in the
39:25
presentation and if UV you can send it into the chat it would be great.
39:31
Um, in that example, I'm using a TTS uh space directly on my hugging face
39:37
profile and I'm just using it to um generate a WAV file that I'm reading
39:44
locally to a local function. Our agent API obviously uh
39:51
handles multi- agent. So we call that end off. This is our way to um handle
39:58
multiple agent in a sequential manner. Meaning like agents don't scale well with the number of tools that you
40:04
provide to them. So you're better off creating more specialized agents and
40:10
deciding let the LLM decide to which agent uh it can end off its work to out
40:17
of a pool of predefined um secondary agents. So you can see that like any go
40:24
the work from one person to another and both having different set of skills. Um if you want to learn more
40:32
about the agent API you can uh just visit the following links. Uh and being
40:38
uh a huge fan of hackathon and having sponsored a lot I can't wait to see what you're going to build uh with our API
40:46
and mission models. Thanks. So, thanks so much, Afrey. Uh,
40:53
they're really really cool to see what Mr. is offering. Um, I'm gonna I'm gonna go ahead and just uh take over now. Um,
Ending notes
41:01
awesome. With that, uh, our time has come to a close and I want to be respectful of of everyone who's here.
41:07
Uh, we've covered a lot of information. Uh if you have questions about any of the stuff that we mentioned uh in terms
41:13
of you know general MCP and agents kind of just theoretical stuff or stuff specific to the hackathon please ask in
41:20
our discord channel. Uh so we've provided uh in the in the comments we've
41:25
we've linked to the discord channel. We'll be there. We'll be answering questions as much as we can during this
41:30
week. And if you have questions about any of the stuff that our sponsors mentioned, uh, Sambboa, Llama Index,
41:37
Mistral, or any of the other ones that are providing credits, uh, feel free to ask in the Discord as well, and we'll
41:42
try to route the questions or they'll be around as well, uh, with office hours as well. Um, so we'll try to get all these
41:48
questions answered. Um, with that, thank you so much. Uh, let's build some amazing
41:58
stuff. All right.
42:36
Thanks so much, Justin. Loved your energy. I I can't hear you. Hold on one
42:43
