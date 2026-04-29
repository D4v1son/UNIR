// Función para generar un ID de categoría aleatorio
function getRandomCategoryId() {
  // Suponiendo que los IDs de categorías van de 1 a 20
  return Math.floor(Math.random() * 20) + 1;
}

// Función para generar una fecha aleatoria en los últimos 5 años
function getRandomDate() {
  const start = new Date();
  start.setFullYear(start.getFullYear() - 5);
  const end = new Date();
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

// Genera un array de 20 documentos con valores aleatorios
const documents = Array.from({ length: 20 }, (_, i) => ({
  _id: ObjectId(), // Genera un nuevo ObjectId
  name: `Producto ${i}`, // Nombre de producto genérico con índice
  primary_category_id: getRandomCategoryId(), // ID de categoría aleatorio
  price: Math.random() * 100 + 50, // Precio aleatorio entre 50 y 150
  variants: {
    "1": { "name": `Color ${i}, Size S` },
    "2": { "name": `Color ${i}, Size M` }
  },
  category_ids: [getRandomCategoryId(), getRandomCategoryId()], // Array de dos IDs de categorías aleatorios
  date_created: getRandomDate() // Fecha de creación aleatoria en los últimos 5 años
}));

// Inserta los documentos en la base de datos
db.collection.insertMany(documents);

