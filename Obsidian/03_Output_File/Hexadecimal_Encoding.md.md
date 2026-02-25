# 🔢 Hexadecimal Wall Encoding

The maze must be written to the output file using a specific hexadecimal encoding system. Each cell is represented by a single hex digit that encodes its walls.

## 🧱 Bit Mapping
A wall being closed sets the bit to `1`, while an open wall is `0`.

- [ ] **Bit 0 (Least Significant Bit, LSB):** North 
- [ ] **Bit 1:** East 
- [ ] **Bit 2:** South 
- [ ] **Bit 3:** West 

## 💡 Examples
- **`3` (Binary `0011`):** The North (`1`) and East (`1`) walls are closed. The walls are open to the South (`0`) and West (`0`).
- **`A` (Binary `1010`):** The East (`1`) and West (`1`) walls are closed. (North is `0`, South is `0`).