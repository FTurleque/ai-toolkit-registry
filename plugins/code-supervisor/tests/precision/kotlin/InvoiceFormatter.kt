package billing

import java.math.BigDecimal
import java.math.RoundingMode

data class InvoiceLine(val label: String, val amount: BigDecimal)

class InvoiceFormatter(private val currency: String) {

    fun total(lines: List<InvoiceLine>): BigDecimal =
        lines.fold(BigDecimal.ZERO) { sum, line -> sum + line.amount }

    fun average(lines: List<InvoiceLine>): BigDecimal {
        if (lines.isEmpty()) {
            return BigDecimal.ZERO
        }
        return total(lines).divide(BigDecimal(lines.size), 2, RoundingMode.HALF_EVEN)
    }

    fun render(lines: List<InvoiceLine>): String {
        val rendered = mutableListOf<String>()
        for (line in lines) {
            rendered.add("${line.label}: ${line.amount} $currency")
        }
        rendered.add("Total: ${total(lines)} $currency")
        return rendered.joinToString(separator = "\n")
    }

    fun parseAmount(text: String): BigDecimal? =
        try {
            BigDecimal(text.trim())
        } catch (e: NumberFormatException) {
            throw IllegalArgumentException("Not an amount: $text", e)
        }
}
