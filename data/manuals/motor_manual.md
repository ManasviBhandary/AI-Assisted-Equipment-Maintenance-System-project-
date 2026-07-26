# Meiden High-Torque Industrial Induction Motor Manual
Document Code: MEC-MAN-MOT-002
Target Equipment: M-201 (High-Torque Drive Motor 1), M-202 (Conveyor Drive Motor 2)

## 1. Operating Parameters & Tolerances
- **Operating Speed**: 1450 RPM / 1750 RPM
- **Nominal Temperature Range**: 45°C - 65°C (Alarm above 80°C)
- **Vibration Tolerance**:
  - Normal: 0.5 - 2.5 mm/s RMS
  - Warning: 3.5 mm/s RMS (Schedule inspection)
  - Danger / Defect Flag: > 4.5 mm/s RMS (Imminent bearing or rotor damage)

## 2. Diagnostics & Maintenance Procedures

### Issue: High Bearing Vibration (> 4.5 mm/s)
**Root Causes**:
1. Inner/outer raceway fatigue in drive-end (DE) bearings.
2. Contaminated or dried out high-temperature grease.
3. Shaft misalignment or worn drive belt.

**Bearing Replacement Procedure**:
1. De-energize motor drive and disconnect coupling/belt guard.
2. Mount hydraulic gear puller onto drive shaft and extract outer bearing collar.
3. Inspect shaft journal for scoring. Clean journal surface with 400-grit emery cloth.
4. Heat new SKF-6210 roller bearing to 110°C using induction bearing heater.
5. Slide bearing onto journal until seated flush against shaft shoulder.
6. Pack bearing cavity 50% full with Polyurea Synthetic High-Temp Grease (Part # MEC-GRS-SYN-01).
7. Reassemble end-bells, torque retaining bolts crosswise to 65 Nm, and perform laser alignment (tolerance < 0.05 mm radial displacement).

### Issue: Motor Frame Resonance & Rotor Imbalance
**Corrective Procedure**:
1. Mount tri-axial accelerometer at DE and NDE bearing housings.
2. Run single-plane dynamic balance utility on portable spectrum analyzer.
3. Attach balance correction weights (M6 stainless set screws) to rotor balance rings at calculated phase angles.
4. Inspect foundation anchor bolts; torque all anchor nuts to 120 Nm.

## 3. Servicing Intervals
- **500 Runtime Hours**: Replenish bearing grease (25 grams per housing).
- **2000 Runtime Hours**: Check drive belt tension with sonic belt tension meter (target 180-200 N).
- **5000 Runtime Hours**: Full overhaul: bearing replacement, stator winding varnish dip, and rotor balance.
