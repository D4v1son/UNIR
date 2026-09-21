document.addEventListener("DOMContentLoaded", iniciar);

function iniciar(){
    comenzando_con_d3()
}

function comenzando_con_d3() {
    d3.select("h1#titulo1")
        .text("Tema 3, escrito con D3")
        .style("color", "red")
    d3.select("p#parrafo1")
        .text("Hoy vamos a aprender a utilizar D3, y esto esta escrito con D3")
        .classed("negrita_cursiva", true)
        .style("color", "red")
    d3.select("p#parrafo2")
        .text("Segundo parrafo que escribo con D3")
        .classed("negrita_cursiva", true)
        .classed("rojo", true)
        // d3.selectAll("p")
        // .style("color", "green")
    d3.select("div#div1")
        .text("texto creado en D3")
        .style("border", "2px red solid")
        .style("background", "yellow")
        .on("click", function() {alert("Mensaje al hacer click en div 1")})
    d3.select("body")
        .append("div")
        .text("texto y espacio (OJO!!) creado en D3")
        .attr("id", "div2")
        .attr("class", "divclass_cyan")
        .on("click", function() {alert("Mensaje al hacer click en div 2")})
}