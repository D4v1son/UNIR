# cargar datos
datos <- read.csv("C:/Users/david/Documents/UNIR/MasterBigDataUNIR/AnalisisInterpretacionDatos/documentacion/bloque3/weather_temp_clean.csv")

# crear 1000 medias muestrales de n=30
set.seed(42)
medias_muestrales <- replicate(1000, mean(sample(datos$Data.Temperature.Avg.Temp, 30, replace=TRUE)))

# media poblacional
media_poblacional <- mean(datos$Data.Temperature.Avg.Temp)

# graficar
hist(
  medias_muestrales, 
  breaks=30, col="skyblue", 
  main="Distribución muestral (n=30)",
  xlab="Media muestral",
  freq=FALSE
)
abline(v=media_poblacional, col="red", lty=2)
lines(density(medias_muestrales), col="blue", lwd=2)
legend("topright", legend=c("Media poblacional"), col="red", lty=2)

#------------------------------------------------------------------------------

# no me ha dado a copiar el diagrama de barras para comparar la media con la poblacion
# ha dicho que lo subira al aula virtual luego, espero no se me olvide