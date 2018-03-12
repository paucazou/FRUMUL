lang "latex" "t(title) l(list) p(position) s(spacing)"
(title : mark "2" "c(chapter) s(section) b(subsection) n(nonumber)"
 (chapter : "\\chapter\{{}}"
  section : "\\section\{{}}"
  subsection : "\\subsection\{{}}"
  nonumber : "c(chapter) s(section) b(subsection)"
  (chapter : "\\chapter*\{{}}"
   section : "\\section*\{{}}"
   subsection : "\\subsection*\{{}}"
  )
 )
 list : "d(description) i(item)"
 (description : mark "2" "\\begin\{description}{}\\end\{description}"
  item : mark "3" "\\item[{}]{}"
 )
 position : mark "2" "l(left) c(center) r(right)"
 (left : "\\begin\{flushleft}{}\\end\{flushleft}"
  right : "\\begin\{flushright}{}\\end\{flushright}"
  center: "\\begin\{center}{}\\end\{center}"
 )
 spacing : mark "1" "b(break) n(newline) p(newpage)"
 newline : "\\newline"
 newpage : "\\newpage"
 (break : "m(medbreak)"
  (medbreak : "\\medbreak"
  )
 )
)
