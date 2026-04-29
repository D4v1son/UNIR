// Función para generar una cantidad aleatoria
function getRandomQty() {
  return Math.floor(Math.random() * 100) + 1; // Cantidades entre 1 y 100
}

// Función para generar un conjunto aleatorio de etiquetas
function getRandomTags() {
  const possibleTags = ["red", "blue", "green", "blank", "plain"];
  return [possibleTags[Math.floor(Math.random() * possibleTags.length)], possibleTags[Math.floor(Math.random() * possibleTags.length)]];
}

// Función para generar dimensiones aleatorias
function getRandomDimensions() {
  return [Math.random() * (30 - 10) + 10, Math.random() * (30 - 10) + 10];
}

// Genera un array de 20 documentos con valores aleatorios
const documents = Array.from({ length: 20 }, (_, i) => ({
  item: `item${i}`, // Nombre de artículo genérico con índice
  qty: getRandomQty(), // Cantidad aleatoria
  tags: getRandomTags(), // Etiquetas aleatorias
  dim_cm: getRandomDimensions() // Dimensiones aleatorias
}));

// Inserta los documentos en la base de datos
db.library.insertMany(documents);
