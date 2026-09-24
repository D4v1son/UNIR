document.addEventListener("DOMContentLoaded", iniciar);

function iniciar(){
    cargarDatos()
        .then(function(datos){
            mostrarDatos(datos)

        })
        .catch(function(error){
            console.error("Error al cargar los datos:", error);
        });
}

function cargarDatos() {
    return d3.json(
    "https://raw.githubusercontent.com/CarmenBigData/datos-publicos/main/partidos.json");

}
function mostrarDatos(datos) {
    console.log("Datos cargados del json");
    window.datosglobal = datos;

    datos.sort(function(x,y){
    // return d3.descending (x.votantes, y.votantes)
        return d3.descending (x.mediaAutoubicacion, y.mediaAutoubicacion)
    })

    d3.select("div#div2")
        .style("border", "2px blue solid")
        //.style("background", "cyan")

    d3.select("div#div2")
        .append("h1")
        .text("Nombre partidos políticos del JSON");
    //const elementoUL = d3.select("div#div2")
    //    .append("ul");
    var elementoUL = d3.select("div#div2")
        .append("ul");

    // Escala de tamaño
    var sizeScale = d3.scaleLinear()
        // .domain([0,3000])
        .domain(d3.extent(datos, function(d) {return d.votantes}))
        .range(["10px", "100px"])

    //Escala de color
    // var colorScale=d3.scaleLinear()
        // .domain([0, 10])
        // .range(["red", "blue"])
    // Escala de color v2
    var colorScale=d3.scaleLinear()
        .domain([0, 5, 10])
        .range(["red", "green", "blue"])

    //datos.forEach(function(d) {
    //    elementoUL
    //        .append("li")
    //        .text(d.partido);
    //});
    elementoUL
        .selectAll("li")
        .data(datos)
        .join("li")
        .text(function(d){return d.partido})
        //.style("font-size", "25px")
        //.style("font-size", function(d){return d.votantes +"px"})
        .style("font-size", function(d) {return sizeScale(d.votantes)})
        .style("color", function(d) {return colorScale(d.mediaAutoubicacion)})
}
