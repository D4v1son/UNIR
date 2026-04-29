// Función para generar un color hexadecimal aleatorio
function getRandomColor() {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

// Función para generar una fecha aleatoria en el último año
function getRandomDate() {
  const start = new Date(new Date().setFullYear(new Date().getFullYear() - 1));
  const end = new Date();
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

// Genera un array de 20 documentos con valores aleatorios
const documents = Array.from({ length: 20 }, (_, i) => ({
  price: 300 + Math.random() * 100, // Precio aleatorio entre 300 y 400
  variants: {
    "1": { "name": `Blue, Small ${i}`, "color": getRandomColor() },
    "2": { "name": `Black, Small ${i}`, "color": getRandomColor() },
    "3": { "name": `Pink, Small ${i}`, "color": getRandomColor() }
  },
  is_active: Math.random() > 0.5, // Activo o no, aleatoriamente
  createdAt: getRandomDate(), // Fecha aleatoria en el último año
  category: ["Accesorios", "Ropa", "Electrónica"][Math.floor(Math.random() * 3)], // Categoría aleatoria
  description: `Descripción del producto ${i}`,
  inStock: Math.random() > 0.5, // En stock o no, aleatoriamente
  stockQuantity: Math.floor(Math.random() * 100) // Cantidad aleatoria en stock
}));

// Inserta los documentos en la base de datos
db.collection.insertMany(documents);
