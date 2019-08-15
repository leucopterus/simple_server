Two server was created. With the help of argparse it is possible to run two
different servers using just one script.
HTML pages are common but divided, the first server has auth.hml and charge.html
 pages.
Another one has just one form.html page. In the first server's auth page 
cookies are set.
Auth cookie set OK when auth page is visited, to delete cookie just push 
'to reset cookie' link.  
HOW TO run task:
0. default ip addresses: `127.0.0.1:8001` and `0.0.0.0:8002`. To change them you should
write the one by one in terminal, then in the second
 terminal write them in reverse order. If you want to use defaults: 
 use `-r` key for reverse (will be shown at the next steps)
1. download all files at the same directory
2. in the first terminal run `python3 myserver.py`
3. in the second terminal run `python3 myserver.py -r`
4. visit [127.0.0.1:8001](http://127.0.0.1:8001) page
