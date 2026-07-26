# Industrial Power Transformer Technical Manual & Service Standard
Document Code: MEC-MAN-TRF-001
Target Equipment: M-101 (Main Power Transformer 1), M-102 (Auxiliary Power Transformer 2)

## 1. Overview & Operational Thresholds
Industrial Power Transformers provide step-down grid isolation and power distribution across Plant Alpha.
- **Normal Operating Temperature**: 50°C - 75°C
- **Warning Threshold**: 85°C
- **Critical Failure Action Level**: > 90°C (Immediate shutdown triggered)
- **Dielectric Oil Pressure**: 4.0 - 5.0 bar
- **Vibration Limit**: < 2.0 mm/s

## 2. Emergency Troubleshooting & Defect Resolution

### Issue: Overheating / Temperature Spike (> 85°C)
**Root Causes**:
1. Cooling fan relay failure or auxiliary radiator blockage.
2. Contaminated dielectric transformer oil.
3. Overloaded secondary tap changer.

**Corrective Procedure**:
1. Isolate primary breaker and attach lockout/tagout (LOTO) key.
2. Inspect relay panel K-04 for tripped thermal breakers or fused contacts.
3. Test cooling fan motor current draw with clamp meter. Replaced cooling fan relay if coil resistance deviates >10% from 240 ohms.
4. Draw 500mL oil sample from lower drain valve and conduct dissolved gas analysis (DGA) and dielectric breakdown testing.
5. If oil breakdown voltage is < 30kV, drain, vacuum filter, and refill with Industrial Oil Spec ISO-32.

### Issue: Winding Overheating & Tap Changer Gasket Leaks
**Corrective Procedure**:
1. Depressurize expansion tank valve V-12.
2. Remove secondary tap changer hatch assembly (16x M12 bolts, torque spec 45 Nm).
3. Replace inner nitrile tap changer gasket (Part # MEC-GSK-TRF-12).
4. Re-calibrate digital thermal protection relay unit to 85°C alarm / 95°C trip.

## 3. Recommended Preventative Maintenance Schedule
- **Monthly**: Thermal imaging scan of primary busbars and Bushing A/B/C connections.
- **Quarterly**: Dielectric oil moisture check and silica gel desiccant color inspection.
- **Annual**: Complete winding insulation resistance test (Megger 5kV test: target > 1000 M-ohms).
