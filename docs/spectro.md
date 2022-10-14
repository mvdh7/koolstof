# Spectrophotometric pH: `ks.spectro`

To calculate pH on the total scale from NIOZ spectrophotometer data:

```python
import koolstof as ks

pH_total = ks.spectro.pH_NIOZ(
    absorbance_578nm,
    absorbance_434nm,
    absorbance_730nm,
    temperature=25,
    salinity=35,
)
```
