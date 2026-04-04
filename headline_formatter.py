import textwrap


def format_headline(title):

    # convert to uppercase
    title = title.upper()

    # remove common filler words
    remove_words = [
        "THE","A","AN","TO","FOR","WITH","OF","IN","ON","AT",
        "AND","FROM","BY","ABOUT","AFTER","BEFORE"
    ]

    words = title.split()

    filtered = [w for w in words if w not in remove_words]

    title = " ".join(filtered)

    # wrap into short lines
    lines = textwrap.wrap(title, width=18)

    return "\n".join(lines[:4])
