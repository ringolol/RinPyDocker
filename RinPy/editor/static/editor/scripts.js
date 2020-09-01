$(document).ready( function() {
  CodeMirror.defineSimpleMode("rinpy", {
    start: [
      {regex: /if|else|for|while|return|var/, token: "keyword"},
      {regex: /(var)(\s+)([a-zA-Z]+)/, token: ["keyword", null, "variable"]},
      {regex: /num|add|integ|div|mult|time|fun/, token: "variable-3"},
      {regex: /print|plot|calc|debug/, token: "variable-2"},
      {regex: /[-+\/*=<>!]+/, token: "operator"},
      {regex: /and|or|not/, token: "atom"},
      {regex: /def/, token: "def"},
      {regex: /{|}/, token: "bracket"},
      {regex: /\(|\)/, token: "bracket"},
      {regex: /\[|\]/, token: "bracket"},
      {regex: /".*?"/, token: "string"},
      {regex: /#.*/, token: "comment"}
    ],
    // meta: {
    //   dontIndentStates: ["comment"],
    //   lineComment: "#"
    // }
  });

  CodeMirror.fromTextArea(document.getElementById("code"), {
    mode:  "rinpy",
    theme: "ayu-dark",
    lineNumbers: true
  });

  let ver_sizes = [75, 25];
  try {
    ver_sizes = JSON.parse( localStorage.getItem('ver_sizes') )
  } finally {}

  let hor_sizes = [25, 75];
  try {
    hor_sizes = JSON.parse( localStorage.getItem('hor_sizes') )
  } finally {}

  Split(['#code_container', '#output_container'], {
    sizes: ver_sizes,
    gutterSize: 10,
    direction: 'vertical',
    snapOffset: 0,
    onDragEnd: function(sizes) {
      localStorage.setItem('ver_sizes', JSON.stringify(sizes))
    },
  })
  Split(['#explorer', '#editor'], {
    sizes: hor_sizes,
    gutterSize: 10,
    direction: 'horizontal',
    // snapOffset: 0,
    minSize: [0, 0],
    onDragEnd: function(sizes) {
      localStorage.setItem('hor_sizes', JSON.stringify(sizes))
    },
  })
});