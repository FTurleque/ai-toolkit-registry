package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import org.junit.jupiter.api.Test;

class ConnectionSettingsTest {

    @Test
    void diagnosticsNeverRepeatTheCredentials() {
        String url = "jdbc:postgresql://reader:fixture-pass@db.internal:5432/shop";
        String shown = ConnectionSettings.publicForm(url);
        assertFalse(shown.contains("fixture-pass"));
        assertEquals("jdbc:postgresql://db.internal:5432/shop", shown);
    }
}
