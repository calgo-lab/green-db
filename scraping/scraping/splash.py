# This Lua script uses the splash API to scroll to the bottom of a webpage.
# This helps to trigger some dynamic JS based requests and get
# a full fletched HTML.
scroll_end_of_page_script = """
function main(splash, args)
    local num_scrolls = 10

    local scroll_to = splash:jsfunc("window.scrollTo")
    local get_body_height = splash:jsfunc(
        "function() {return document.body.scrollHeight;}"
    )
    assert(splash:go{args.url, headers=args.headers})
    splash:wait(args.wait)

    for _ = 1, num_scrolls do
        local height = get_body_height()
        for i = 1, 10 do
            scroll_to(0, height * i/10)
            splash:wait(args.wait)
        end
        splash:wait(args.wait)
    end
    splash:wait(args.wait)
    return {
        url = splash:url(),
        html = splash:html(),
    }
end
"""
