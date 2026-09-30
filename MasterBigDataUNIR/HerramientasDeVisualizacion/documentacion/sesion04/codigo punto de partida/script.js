document.addEventListener("DOMContentLoaded", iniciar);

// ************************************
// Definicion de variables
// ************************************

// Dimensiones del SVG
var width = 600;
var height = 450;
// Margenes para que se vean bien todos los círculos
var margen={
    arriba:60,
    abajo:35,
    izquierda:40,
    derecha:50
}

// ************************************


// ************************************
// Definicion de funciones
// ************************************


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

    // ************************************
    // Definicion de variables
    // ************************************

    // Configuramos el SVG
    var grafico_svg = d3.select("svg#miSVG")
        .attr("width", width)
        .attr("height", height)
        .style("border", "5px solid red")

    // Creamos la escala del eje Y
    var Y_Scale = d3.scaleLinear()
        .domain(d3.extent(datos, function(d) {return d.votantes}))
        .range([height-margen.abajo, margen.arriba])
    
    // Creamos la escala de tamaño de los círculos según numero de votantes
    var sizeScale = d3.scaleLinear()
        .domain(d3.extent(datos, function(d) {return d.votantes}))
        .range([5, 50])

    // Creamos la escala del eje X
    var X_Scale = d3.scaleLinear()
        .domain([0, 10])
        .range([margen.izquierda, width-margen.derecha])
    
    // Creamos la escala de color según el espectro político
    var colorScale = d3.scaleLinear()
        .domain([0, 5, 10])
        .range(["red", "green", "blue"])
    
    // Definimos el eje X
    var eje_X = d3.axisBottom(X_Scale)
    // Definimos el eje Y
    var eje_Y = d3.axisLeft(Y_Scale)

    // ************************************
    
    // Dibujamos haciendo el JOIN con los datos
    grafico_svg.selectAll("circle")
        .data(datos)
        .join("circle")
        // .attr("cx", "60")
        .attr("cx", function(d) {return X_Scale(d.mediaAutoubicacion)})
        // .attr("cy", "230")
        .attr("cy", function(d) {return Y_Scale(d.votantes)})
        // .attr("r", "50")
        .attr("r", function(d) {return sizeScale(d.votantes)})
        // .attr("fill", "red")
        .attr("fill", function(d) {return colorScale(d.mediaAutoubicacion)});

    // Dibujamos el eje X, dentro de un grupo "g" que está dentro del svg
    grafico_svg.append("g")
        .attr("transform", "translate (0," + (height-margen.arriba/2) + ")")
        .call (eje_X)

    // Dibujamos el eje Y, dentro de un grupo "g" que está dentro del svg
    grafico_svg.append("g")
        .attr("transform", "translate (" + margen.izquierda + ",0)")
        .call (eje_Y)
}

