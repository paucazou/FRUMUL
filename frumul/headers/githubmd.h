//*Markdown GitHub flavor*//
lang "ghmd" "h(header) i(italic) b(bold) k(link) q(blockquote) c(incode) f(codefencing) m(image) l(list) e(level) o(crossedout) t(table)"
(
 bold : mark "2" "**{}**"
 italic : mark "2" "*{}*"
 header : mark "2" "123456"
 (1 : "#{}EOL"
  2 : "##{}EOL"
  3 : "###{}EOL"
  4 : "####{}EOL"
  5 : "#####{}EOL"
  6 : "######{}EOL"
 )
 header : "#{}EOL" //* shortcut for h1 *//
 link : mark "3" "[{}]({})"
 blockquote : mark "2" "> {}EOL"
 incode : mark "2" "`{}`"
 codefencing : mark "3" "```{}EOL{}EOL```"
 image : mark "3" "![{}]({})"
 crossedout : mark "2" "~~{}~~"
 level : mark "1" "123456" //* the level allows user to indent lists *//
 (1 : "  " //* Actually, levels start with 0 *//
  2 : "    "
  3 : "      "
  4 : "        "
  5 : "          "
  6 : "            "
 )
 list : mark "2" "o(ordered) b(bullet) d(dash) i(incompletetask) c(completetask)"
 (ordered : "l. {}EOL"
  bullet : "* {}EOL"
  dash : "- {}EOL"
  completetask : "- [x] {}EOL"
  incompletetask : "- [ ] {}EOL"
 )
 table : "b(box) s(sep)"
 ( box : mark "2" "|{} "
   sep : mark "1" "|-" //* tests needed *//
 )
) //* authorize files to define twice or more; authorize multiple names of langs : lang "md/markdown" for instance ; create more dynamic definition *//
