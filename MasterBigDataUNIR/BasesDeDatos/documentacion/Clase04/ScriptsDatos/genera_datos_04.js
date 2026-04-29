// Función para generar una cantidad aleatoria entre 1 y 100
function getRandomQty() {
  return Math.floor(Math.random() * 100) + 1;
}

// Función para generar un arreglo de objetos 'instock' con cantidades aleatorias para almacenes A, B, C
function getRandomInStock() {
  return [
    { warehouse: "A", qty: getRandomQty() },
    { warehouse: "B", qty: getRandomQty() },
    { warehouse: "C", qty: getRandomQty() }
  ];
}

// Genera un array de 20 documentos con valores aleatorios
const documents = Array.from({ length: 20 }, (_, i) => ({
  item: `item${i}`, // Nombre de artículo genérico con índice
  instock: getRandomInStock() // Arreglo de objetos 'instock' con cantidades aleatorias
}));

// Inserta los documentos en la base de datos
db.library.insertMany(documents);
