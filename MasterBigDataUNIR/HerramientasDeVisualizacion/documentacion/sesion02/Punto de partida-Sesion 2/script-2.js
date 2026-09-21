document.addEventListener("DOMContentLoaded", iniciar);

function iniciar(){
    comenzando_con_d3()
}

function comenzando_con_d3() {
    d3.select("h1#titulo1")
        .text("Tema 3: Ya soy un CRACK con D3")
        .style("color", "red")

    d3.select("p#parrafo1")
        .text("Ya soy un CRACK con D3")
        .style("color", "red")
    
    d3.select("p#parrafo1")
        .text("Vamos a leer un fichero de datos y crear una lista con D3 basada en esos datos")
        .classed("negrita_cursiva", true)
        .style("color", "red")
    }
