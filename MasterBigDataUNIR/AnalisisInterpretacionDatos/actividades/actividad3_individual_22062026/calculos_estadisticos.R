
# Importo los datos
library(dplyr)

datos <- read.csv("ecommerce_customer_behavior_dataset.csv")



# -----------
# Escenario A
# -----------

# Primer análisis de los datos
summary(datos$Delivery_Time_Days)
sd(datos$Delivery_Time_Days)

# Representación gráfica de los datos
hist(datos$Delivery_Time_Days,
     main = "Distribución del tiempo de entrega",
     xlab = "Tiempo de entrega (días)",
     col = "steelblue",
     freq = TRUE)

abline(v = mean(datos$Delivery_Time_Days), col = "red", lwd = 2, lty = 2)

# Contraste de hipótesis caso A
t.test(datos$Delivery_Time_Days, mu = 5, alternative = "greater")


# -----------
# Escenario B
# -----------

# Primer análisis de los datos
tapply(datos$Total_Amount, datos$Is_Returning_Customer, summary)
tapply(datos$Total_Amount, datos$Is_Returning_Customer, sd)
table(datos$Is_Returning_Customer)

# Representación gráfica de los datos
boxplot(Total_Amount ~ Is_Returning_Customer,
        data = datos,
        main = "Gasto total por tipo de cliente (escala log)",
        xlab = "Cliente recurrente",
        ylab = "Importe total del pedido (log)",
        col = c("lightcoral", "steelblue"),
        log = "y")

# Contraste de hipótesis caso B
t.test(Total_Amount ~ Is_Returning_Customer,
       data = datos,
       alternative = "less")
