# Icon Mapping Configuration

This file maps bid icon subjects to deployment icon subjects for PDF conversion.
Updated based on actual subjects discovered in BidMap.pdf.

## Mapping Rules

- Bid icons represent generic/placeholder equipment in venue bid maps
- Deployment icons represent specific equipment models to be installed
- Multiple bid icons may map to the same deployment icon type
- Legend items and measurements are excluded from conversion

| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| Artist - Indoor Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Artist - Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Artist - High Density Wi-Fi Access Point | AP - Cisco 9166I | Access Points |
| Artist - High Density Directional Wi-Fi Access Point | AP - Cisco 9166D | Access Points |
| Artist - Outdoor Wi-Fi Access Point | AP - Cisco MR78 | Access Points |
| Artist - Ethernet Hardline | HL - Artist | Hardlines |
| Artist - High Capacity Ethernet Hardline | HL - Artist | Hardlines |
| Production - Indoor Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Production - Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Production - Medium Density Wi-Fi Access Point | AP - Cisco 9166I | Access Points |
| Production - High Density Wi-Fi Access Point | AP - Cisco 9166I | Access Points |
| Production - Medium Density Directional Wi-Fi Access Point | AP - Cisco 9166D | Access Points |
| Production - High Density Directional Wi-Fi Access Point | AP - Cisco 9166D | Access Points |
| Production - Outdoor Wi-Fi Access Point | AP - Cisco MR78 | Access Points |
| Production - Ethernet Hardline | HL - Production | Hardlines |
| Production - High Capacity Ethernet Hardline | HL - Production | Hardlines |
| Point-of-Sale - Indoor Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Point-of-Sale - Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Point-of-Sale - High Density Wi-Fi Access Point | AP - Cisco 9166I | Access Points |
| Point-of-Sale - High Density Directional Wi-Fi Access Point | AP - Cisco 9166D | Access Points |
| Point-of-Sale - Outdoor Wi-Fi Access Point | AP - Cisco MR78 | Access Points |
| Point-of-Sale - Ethernet Hardline | HL - PoS | Hardlines |
| Point-of-Sale - High Capacity Ethernet Hardline | HL - PoS | Hardlines |
| Access Control - Indoor Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Access Control - Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Access Control - High Density Wi-Fi Access Point | AP - Cisco 9166I | Access Points |
| Access Control - High Density Directional Wi-Fi Access Point | AP - Cisco 9166D | Access Points |
| Access Control - Outdoor Wi-Fi Access Point | AP - Cisco MR78 | Access Points |
| Access Control - Ethernet Hardline | HL - Access Control | Hardlines |
| Access Control - High Capacity Ethernet Hardline | HL - Access Control | Hardlines |
| Sponsor - Indoor Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Sponsor - Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
| Sponsor - High Density Wi-Fi Access Point | AP - Cisco 9166I | Access Points |
| Sponsor - High Density Directional Wi-Fi Access Point | AP - Cisco 9166D | Access Points |
| Sponsor - Outdoor Wi-Fi Access Point | AP - Cisco MR78 | Access Points |
| Sponsor - Ethernet Hardline | HL - Sponsor | Hardlines |
| Sponsor - High Capacity Ethernet Hardline | HL - Sponsor | Hardlines |
| High Density - Wi-Fi Access Point | AP - Cisco 9166I | Access Points |
| High Density - Stadium Wi-Fi Access Point | AP - Cisco DB10 | Access Points |
| Hyper Directional Stadium Access Point | AP - Cisco DB10 | Access Points |
| Hyper Directional Wi-Fi 7 Stadium Access Point | AP - Cisco Marlin 4 | Access Points |
| Distribution - Compact Edge Switch | SW - Cisco Micro 4P | Switches |
| Distribution - Edge Switch | SW - Cisco 9200 12P | Switches |
| Distribution - Clair Custom IDF Rack | SW - IDF Cisco 9300 24X | Switches |
| Distribution - Clair Network Core Rack Compact | DIST - Micro NOC | Switches |
| Distribution - Clair Network Core Rack - Compact | DIST - Micro NOC | Switches |
| Distribution - Clair Network Core Rack - High-Capacity | DIST - Standard NOC | Switches |
| Distribution - Cellular Gateway | DIST - MikroTik Hex | Switches |
| Distribution - ISP | DIST - Starlink | Switches |
| INFRAS - Compact Edge Switch | SW - Cisco Micro 4P | Switches |
| INFRAS - Edge Switch | SW - Cisco 9200 12P | Switches |
| INFRAS - Clair IDF Rack | SW - IDF Cisco 9300 24X | Switches |
| INFRAS - Clair Network Core Rack - Compact | DIST - Mini NOC | Switches |
| INFRAS - Clair Network Core Rack - High-Capacity | DIST - Standard NOC | Switches |
| INFRAS - Point-to-Point Transeiver | P2P - Ubiquiti NanoBeam | Point-to-Points |
| INFRAS - Point-to-Multipoint Transeiver | P2P - Ubiquiti LiteAP | Point-to-Points |
| INFRAS - High Capacity Point-to-Point Transeiver | P2P - Ubiquiti GigaBeam | Point-to-Points |
| INFRAS - High Capacity Point-to-Multipoint Transeiver | P2P - Ubiquiti GigaBeam LR | Point-to-Points |
| INFRAS - VoIP Phone | VOIP - Yealink T29G | IoT |
| INFRAS - Conference VoIP Phone | VOIP - Yealink CP965 | IoT |
| INFRAS - Starlink Satellite Internet | DIST - Starlink | Switches |
| INFRAS - Production IT & Radio Programming Package | DIST - Pelican NOC | Switches |
| Ethernet Hardline | HL - General Internet | Hardlines |
| AV - Ethernet Hardline | HL - Audio | Hardlines |
| Emergency Announce - Ethernet Hardline | HL - Emergency Announce System | Hardlines |
| High Capacity - Ethernet Hardline | HL - WAN | Hardlines |
| CCTV - Axis Outdoor PTZ Camera | CCTV - AXIS P5655-E | IoT |
| CCTV - Axis Camera Workstation | CCTV - AXIS S9302 | IoT |
| CCTV - CCTV Network Video Recorder | CCTV - AXIS S9302 | IoT |
| EAS - Clair Emergency Announce, Command Control Unit | EAS - Command Unit | IoT |
| EAS - Clair Emergency Announce, Read Only Tablet | EAS - Laptop | IoT |
| EAS - Clair Emergency Announce, Trigger Box | EAS - Trigger Box | IoT |
| IPTV - IPTV Set-Top Box \(DMP\ | IPTV - BrightSign XT1144 | IoT |
| IPTV - Low Latency IPTV Encoder | IPTV - BrightSign XT1144 | IoT |
| Fiber Junction | INFRA - Fiber Patch Panel | Miscellaneous |
| CBL - CAT6 | HL - General Internet | Hardlines |
| CBL - Tactical Fiber, Single Mode, TAC2, ST, 100' \(30m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC2, ST, 250' \(76m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC2, ST, 500' \(152m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC2, ST, 1000' \(304m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC4, ST, 250' \(76m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC4, ST, 500' \(152m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC4, ST, 1000' \(304m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC12, ST, 250' \(76m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC12, ST, 500' \(152m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC12, ST, 1000' \(304m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC24, ST, 250' \(76m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC24, ST, 500' \(152m\ | FIBER | Cables |
| CBL - Tactical Fiber, Single Mode, TAC24, ST, 1000' \(304m\ | FIBER | Cables |
