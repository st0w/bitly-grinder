bitly-grinder
=============

About
-----

After seeing Daniel Crowley's entertaining talk at ShmooCon 2011 on URL
shorteners, I'd wanted to put together something to do some URL grinding
and harvesting myself.  Which led to this project.  Because people use
URL shortening services without realizing that things they shorten can
be easily discovered, there's a lot of stuff out there.

At this point, the project is probably not terribly accurately named - it
supports pretty much any kind of URL shortening/redirection service.  In
the current state, it basically works by passing a URL to the grinder,
and the grinder then tries every iteration created by fuzzing the last two
characters.  By default, tries upper and lowercase letters and digits.  You
can change this by altering `CHARSET`.

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
