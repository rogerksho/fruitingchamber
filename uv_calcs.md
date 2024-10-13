# UV-C calcs

*references: https://klaran.com/how-much-time-is-required-for-surface-disinfection-in-your-application*

**UVC LED:**
- 0.2W UVC
- Name:3535 UVC+UVA Stterilization lamp beads
- Bilateral:265nm
- Current:30-60mA
- Voltage:5-6V
- power:0.2-0.35W
- Angle: 120degree

**irradiation area:**
- assume cone
- 120 degrees
- by geometry, the following ratio holds true: $r/h = tan(120\degree) = 1.732$
- therefore, base area is $A=\pi r^2=\pi(1.732h)^2$
- where $h$ is distance away from irradiated surface

**irradiation time:**
- units are in mW/cm^2
- LED is 200 mW !!!!!!!!!!!!!!! actual flux is probably much less
- requires 5.2 mJ/cm^2 for 99% reduction
- [mJ/cm^2] = [mW/cm^2]*[irriadiated_time]

**quick calcs**
- estimated distance of 30 cm away from target surface
- $A=\pi r^2=\pi(1.732\cdot 30)^2 = 8481.8 \ cm^2$
- power per area = 200/8481.8 = 0.0236 mW/cm^2
- exposure time = 5.2/0.0236 = 220.5 s
    - round up to 5 minutes, 300 seconds