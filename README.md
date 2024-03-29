bitly-grinder
=============

About
-----

After seeing Daniel Crowley's entertaining talk at ShmooCon 2011 on URL
shorteners, I'd wanted to put together something to do some URL grinding
and harvesting myself.  Which led to this project.  Because people use
URL shortening services without realizing that things they shorten can
be easily discovered (the services do not promise or even suggest that they
provide privacy, this isn't their fault), there's a lot of stuff out there.

At this point, the project is probably not terribly accurately named - it
supports pretty much any kind of URL shortening/redirection service.  In
the current state, it basically works by passing a URL to the grinder,
and the grinder then tries every iteration created by fuzzing the last two
characters.  By default, tries upper and lowercase letters and digits.  You
can change this by altering `CHARSET`.

The grinder will try every URL in sequence, and it will track every URL
it encounters during resolution.  It also tracks the status code encountered
when retrieving the final URL in the resolution process.  It will follow as
many redirections as it encounters starting with the base URL.  It also
tracks the content-type obtained at the final URL in the resolution
process.

Results are stored in an SQLite database, named `bitly-grinder.db` in the
same directory as the script is run from.

Results can be browsed via the embedded simple HTTP server, which runs on
port 8000 by default.  Just run `grinder_http_server.py` and then browse to
`http://localhost:8000`.  The following paths exist by default:

* / -- (or any unknown URL) Displays URLs and all paths in the resolution
  process that ultimately resulted in status 200.
* /all -- Displays every result obtained.
* /nonhtml -- Displays only results that were valid (status 200) and
  not of content-type text/html
* /nonhtml-all -- Displays all results with content-type other than
  text/html, regardless of status.
* /images -- Displays all images that were found.

Dependencies
------------

* [DictShield](http://github.com/j2labs/dictshield) -- DictShield, an
  awesome library that provides typed dictionary support and object
  modeling/validation.

Future and Contributing
-----------------------

I've thought of a number of random things that would be cool to add to the
project at some point.  If you've got more or you're interested in
contributing, please get in touch with me.

* Extend the HTTP server for result browsing, possibly with an AJAXy UI
* Provide statistics on what sites have the most shortened URLs
* Track history - resolution path + destination URLs over time
* Some kind of remote control mechanism, so that grinding can be distributed
  across a number of remote nodes, e.g. AWS.
* Randomization of grinding URLs
