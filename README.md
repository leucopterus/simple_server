Two servers were created. They are launched on different ip addresses. 
The first server has and processes only one html page - form.html.
The method do_Options was added, just to prevent some errors.
The js script was added to send the form automatically to the second server.
You can check that the script works in inspector (F12), 
also in the second sever's response in terminal.
Another one has auth and charge pages. 
In the first server's auth page cookies is set. 
Auth cookie set OK when auth page is visited, 
to reset cookie just push 'to reset cookie' link.

## HOW TO run task:
1. download all files at the same directory
2. in the first terminal run `myserver.py` python script
3. in the second terminal run `myserver2.py` python script
4. visit [0.0.0.0:8002](0.0.0.0:8002) page
