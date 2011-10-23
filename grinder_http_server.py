#!/usr/bin/env python
# ---*< bitly_grinder/grinder_http_server.py >*-------------------------------
# Copyright (C) 2011 st0w
# 
# This module is part of bit.ly Grinder and is released under the MIT License.
# Please see the LICENSE file for details.
#
"""Quick and dirty HTTP server for browsing results

Created on Oct 22, 2011

"""
# ---*< Standard imports >*---------------------------------------------------
import BaseHTTPServer
from cgi import escape
import SocketServer

# ---*< Third-party imports >*------------------------------------------------

# ---*< Local imports >*------------------------------------------------------
from db import get_results, get_results_by_content_type, init_db_conn

# ---*< Initialization >*-----------------------------------------------------
PORT = 8000

# ---*< Code >*---------------------------------------------------------------
class BGHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Simple GET handler for bit.ly grinder"""
    def print_links(self, results):
        """Displays a list of BitlyUrl objects as links
        
        :param results: `iterable` that provides `BitlyUrl` objects
        :rtype: None
        
        """
        for bitly in results:
            self.wfile.write('<li>%d - %s - ' %
                             (bitly.status,
                              bitly.content_type))

            for u in bitly.path:
                self.wfile.write('<a href="%s">%s</a><br />' %
                                 (escape(u, quote=True),
                                  escape(u, quote=True)))

            self.wfile.write('</li>\n')


    def do_GET(self):
        # Not the most efficient way to connect to the DB, would be
        # better to connect once and retain, but, I'm lazy.
        db = init_db_conn()

        # Pop off headers
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write("<html><head><title>bit.ly grinder</title></head>")
        self.wfile.write("<body><ul>")

        if self.path == '/images':
            """Show all matching images"""
            results = get_results_by_content_type(db, content_type='image/%')
            for res in results:
                self.wfile.write('<br><img src="%s" />%s - %s<br>\n' %
                                 (res.path[-1], res.path[0],
                                  res.path[-1]))

        elif self.path == '/nonhtml':
            results = get_results(db, status=200, exclude_content='text/html')
            self.print_links(results)

        elif self.path == '/nonhtml-all':
            results = get_results(db, exclude_content='text/html')
            self.print_links(results)

        elif self.path == '/all':
            results = get_results(db)
            self.print_links(results)

        else:
            results = get_results(db, status=200)
            self.print_links(results)

        self.wfile.write("</ul></body></html>")


def serve(port):
    """Simple HTTP server for browsing bit.ly grinder results"""
    Handler = BGHandler

    httpd = SocketServer.TCPServer(("", port), Handler)

    print "serving at port", port
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


def main():
    """Just launches the server"""
    serve(PORT)


if __name__ == "__main__":
    main()

__all__ = (serve)
