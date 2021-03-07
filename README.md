# HW1332 Scraper
The counterpart. The complement. The yin to [the client's](https://github.com/preyneyv/hw1332-client) yang.

This is a scraper that runs once every 10 minutes to fetch the latest gists and submissions to the class Piazza board. After extracting these links, the scraper pushes them to a Gist that serves as the "index", the "glossary", the "source of all that is good and true". If you want, you can view the Gist as it updates here. GATech students only. Sorry outsiders, you're not cool enough.

https://github.gatech.edu/gist/pnutalapati3/b9840d3e5599a5015db7d56b4fe25cf3/

The reason for this rather interesting use of Gists is simple: I don't want to pay for server hosting.

Once the data hits the Gist, it's accessible to all authenticated clients, which then proceed to display and consume the data however they want to. The Gist ID is hardcoded into all the clients so they know where to look.

`.env.example` has the required environment variables to make the whole thing work. I *definitely* have my real password in there.
