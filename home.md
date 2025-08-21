<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Oracle OTM - C209 Catering Delivery Slip</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
<style>
  body { font-family: Inter, Arial, sans-serif; margin: 24px; color: #111827; }
  .header { display: flex; justify-content: space-between; align-items: center; }
  .title { font-size: 20px; font-weight: 700; }
  .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; margin-top: 16px; }
  .card { border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; background: #ffffff; }
  .card h3 { margin: 0 0 8px 0; font-size: 14px; color: #111827; }
  .row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
  .field { font-size: 12px; }
  .label { color: #6B7280; margin-bottom: 4px; }
  .value input, .value textarea { 
    width: 100%; 
    border: 1px solid #D1D5DB; 
    border-radius: 4px; 
    padding: 4px 8px; 
    font-size: 12px; 
    font-weight: 600; 
    color: #111827;
    background: #ffffff;
    box-sizing: border-box;
  }
  .value textarea { resize: vertical; min-height: 60px; }
  .full { grid-column: span 6; }
  .half { grid-column: span 3; }
  .third { grid-column: span 2; }
  .two { grid-column: span 2; }
  .four { grid-column: span 4; }
  .signatures { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
  .signature-box { border: 1px solid #D1D5DB; border-radius: 8px; padding: 12px; min-height: 80px; }
  .signature-title { font-weight: 600; margin-bottom: 8px; }
  .signature-line { border-bottom: 1px solid #D1D5DB; margin: 8px 0; height: 40px; }
  .barcode, .qrcode { text-align: center; }
  .no-print { display: block; }
  @media print { .no-print { display: none !important; } }
</style>
</head>
<body>
  <div class="header">
    <div style="display:flex; align-items:center; gap:16px;">
      <img src="Oracle-Logo.png" alt="Oracle" style="height:36px;"/>
      <img src="Viva_Logotipo-01.png" alt="Viva Airline" style="height:36px;"/>
      <div>
        <div class="title">C209 Catering Delivery Slip</div>
      </div>
    </div>
    <div>
      <div id="barcode" class="barcode"></div>
      <div id="qrcode" class="qrcode" style="margin-top:8px;"></div>
    </div>
  </div>

  <div class="grid">
    <!-- Delivery Information -->
    <div class="card" style="grid-column: span 6;">
      <h3>Delivery Information</h3>
      <div class="row">
        <div class="field half">
          <div class="label">Delivery Slip Number</div>
          <div class="value"><input type="text" id="delivery_slip_number" placeholder="Ej. DS-0001"></div>
        </div>
        <div class="field half">
          <div class="label">OTM Shipment ID</div>
          <div class="value"><input type="text" id="otm_shipment_id" placeholder="Ej. OTM-123456"></div>
        </div>
        <div class="field third">
          <div class="label">Order Number</div>
          <div class="value"><input type="text" id="order_number" placeholder="Ej. ON12345"></div>
        </div>
        <div class="field third">
          <div class="label">Purchase Order</div>
          <div class="value"><input type="text" id="purchase_order" placeholder="Ej. PO124567"></div>
        </div>
        <div class="field third">
          <div class="label">Date Delivered</div>
          <div class="value"><input type="date" id="date_delivered" value="2025-08-21"></div>
        </div>
        <div class="field third">
          <div class="label">Time Delivered</div>
          <div class="value"><input type="time" id="time_delivered" value="13:35"></div>
        </div>
        <div class="field third">
          <div class="label">Time Zone</div>
          <div class="value"><input type="text" id="time_zone" placeholder="UTC"></div>
        </div>
      </div>
    </div>

    <!-- Flight Information -->
    <div class="card" style="grid-column: span 6;">
      <h3>Flight Information</h3>
      <div class="row">
        <div class="field half">
          <div class="label">Airline</div>
          <div class="value"><input type="text" id="airline" placeholder="VIVA"></div>
        </div>
        <div class="field half">
          <div class="label">Flight Number</div>
          <div class="value"><input type="text" id="flight_number" placeholder="Ej. VB12345"></div>
        </div>
        <div class="field half">
          <div class="label">Tail Number</div>
          <div class="value"><input type="text" id="tail_number" placeholder="Ej. XA-1357"></div>
        </div>
        <div class="field half">
          <div class="label">Flight Date</div>
          <div class="value"><input type="date" id="flight_date"></div>
        </div>
        <div class="field third">
          <div class="label">Departure Airport</div>
          <div class="value"><input type="text" id="dep_airport" placeholder="Ej. MEX"></div>
        </div>
        <div class="field third">
          <div class="label">Arrival Airport</div>
          <div class="value"><input type="text" id="arr_airport" placeholder="Ej. LAX"></div>
        </div>
        <div class="field third">
          <div class="label">Gate</div>
          <div class="value"><input type="text" id="gate" placeholder="Ej. G12"></div>
        </div>
        <div class="field third">
          <div class="label">STD</div>
          <div class="value"><input type="datetime-local" id="std"></div>
        </div>
        <div class="field third">
          <div class="label">ETD</div>
          <div class="value"><input type="datetime-local" id="etd"></div>
        </div>
        <div class="field third">
          <div class="label">STA</div>
          <div class="value"><input type="datetime-local" id="sta"></div>
        </div>
        <div class="field third">
          <div class="label">ETA</div>
          <div class="value"><input type="datetime-local" id="eta"></div>
        </div>
        <div class="field third">
          <div class="label">Route</div>
          <div class="value"><input type="text" id="route" placeholder="Ej. MEX-LAX"></div>
        </div>
        <div class="field third">
          <div class="label">Aircraft Type</div>
          <div class="value"><input type="text" id="aircraft_type" placeholder="Ej. A321"></div>
        </div>
      </div>
    </div>
    <!-- Vehicle Information -->
    <div class="card" style="grid-column: span 6;">
      <h3>Vehicle Information</h3>
      <div class="row">
        <div class="field half">
          <div class="label">Vehicle ID</div>
          <div class="value"><input type="text" id="vehicle_id" placeholder="Ej. TRK-45"></div>
        </div>
        <div class="field half">
          <div class="label">License Plate</div>
          <div class="value"><input type="text" id="license_plate" placeholder="Ej. 8ABC123"></div>
        </div>
        <div class="field half">
          <div class="label">Trailer ID</div>
          <div class="value"><input type="text" id="trailer_id" placeholder="Ej. TRL-77"></div>
        </div>
        <div class="field half">
          <div class="label">Refrigeration Unit ID</div>
          <div class="value"><input type="text" id="refrig_unit_id" placeholder="Ej. CARRIER-01"></div>
        </div>
        <div class="field third">
          <div class="label">Temp Start (°C)</div>
          <div class="value"><input type="number" id="temp_start_c" placeholder="4"></div>
        </div>
        <div class="field third">
          <div class="label">Temp End (°C)</div>
          <div class="value"><input type="number" id="temp_end_c" placeholder="2"></div>
        </div>
        <div class="field third">
          <div class="label">Load ID</div>
          <div class="value"><input type="text" id="load_id" placeholder="Ej. CARGA-999"></div>
        </div>
        <div class="field third">
          <div class="label">Seal Pre</div>
          <div class="value"><input type="text" id="seal_pre" placeholder="Ej. SEAL123"></div>
        </div>
        <div class="field third">
          <div class="label">Seal Post</div>
          <div class="value"><input type="text" id="seal_post" placeholder="Ej. SEAL456"></div>
        </div>
        <div class="field third">
          <div class="label">Dock Bay</div>
          <div class="value"><input type="text" id="dock_bay" placeholder="Ej. Dock 3"></div>
        </div>
        <div class="field third">
          <div class="label">Mileage In</div>
          <div class="value"><input type="number" id="mileage_in" placeholder="Ej. 120345"></div>
        </div>
        <div class="field third">
          <div class="label">Mileage Out</div>
          <div class="value"><input type="number" id="mileage_out" placeholder="Ej. 120367"></div>
        </div>
      </div>
    </div>

    <!-- Driver Information -->
    <div class="card" style="grid-column: span 6;">
      <h3>Driver Information</h3>
      <div class="row">
        <div class="field half">
          <div class="label">Driver Name</div>
          <div class="value"><input type="text" id="driver_name" placeholder="Ej. Juan Perez"></div>
        </div>
        <div class="field half">
          <div class="label">Driver ID</div>
          <div class="value"><input type="text" id="driver_id" placeholder="Ej. DRV-001"></div>
        </div>
        <div class="field half">
          <div class="label">Company</div>
          <div class="value"><input type="text" id="company" placeholder="Ej. Aerococina"></div>
        </div>
        <div class="field half">
          <div class="label">Driver Phone</div>
          <div class="value"><input type="tel" id="driver_phone" placeholder="Ej. 555-0100"></div>
        </div>
        <div class="field full">
          <div class="label">Driver Email</div>
          <div class="value"><input type="email" id="driver_email" placeholder="Ej. driver@example.com"></div>
        </div>
      </div>
    </div>

    <!-- Received By Information -->
    <div class="card" style="grid-column: span 6;">
      <h3>Received By</h3>
      <div class="row">
        <div class="field half">
          <div class="label">Receiver Name</div>
          <div class="value"><input type="text" id="recv_name" placeholder="Ej. Marcos Flores"></div>
        </div>
        <div class="field half">
          <div class="label">Role</div>
          <div class="value"><input type="text" id="recv_role" placeholder="Ej. Mayor"></div>
        </div>
        <div class="field half">
          <div class="label">Location</div>
          <div class="value"><input type="text" id="recv_location" placeholder="Ej. Gate 12"></div>
        </div>
        <div class="field half">
          <div class="label">Badge Number</div>
          <div class="value"><input type="text" id="recv_badge" placeholder="Ej. 563479"></div>
        </div>
      </div>
    </div>
        <!-- Catering Items -->
    <div class="card" style="grid-column: span 12;">
      <h3>Catering Items</h3>
      <div class="row">
        <div class="field third">
          <div class="label">Barset Number</div>
          <div class="value"><input type="text" id="barset_number" placeholder="Ej. VB5512"></div>
        </div>
        <div class="field third">
          <div class="label">Packing Standard</div>
          <div class="value"><input type="text" id="packing_standard" placeholder="Ej. PP_DIC24(EMPIEZA EL 12122024)"></div>
        </div>
        <div class="field third">
          <div class="label">Manifest</div>
          <div class="value"><input type="text" id="manifest" placeholder="Ej. VBMEX269382"></div>
        </div>
        <div class="field third">
          <div class="label">Ovens</div>
          <div class="value"><input type="number" id="ovens" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Atlas Box</div>
          <div class="value"><input type="number" id="atlas_box" placeholder="4"></div>
        </div>
        <div class="field third">
          <div class="label">Trolleys</div>
          <div class="value"><input type="number" id="trolleys" placeholder="2"></div>
        </div>
        <div class="field third">
          <div class="label">Waste Carts</div>
          <div class="value"><input type="number" id="waste_carts" placeholder="1"></div>
        </div>
        <div class="field third">
          <div class="label">Dry Ice (kg)</div>
          <div class="value"><input type="number" step="0.1" id="dry_ice_kg" placeholder="0.0"></div>
        </div>
        <div class="field third">
          <div class="label">Ice (kg)</div>
          <div class="value"><input type="number" step="0.1" id="ice_kg" placeholder="1.0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals Y</div>
          <div class="value"><input type="number" id="meals_y" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals P</div>
          <div class="value"><input type="number" id="meals_p" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals J</div>
          <div class="value"><input type="number" id="meals_j" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals F</div>
          <div class="value"><input type="number" id="meals_f" placeholder="0"></div>
        </div>
        <div class="field half">
          <div class="label">Special Meals</div>
          <div class="value"><input type="text" id="special_meals" placeholder="Ej. Vegetarian, Kosher, etc."></div>
        </div>
        <div class="field half">
          <div class="label">Special Beverages</div>
          <div class="value"><input type="text" id="special_beverages" placeholder="Ej. Wine, Champagne, etc."></div>
        </div>
        <div class="field four">
          <div class="label">Items Detail</div>
          <div class="value"><textarea id="items_detail" placeholder="Selected catering items will appear here..."></textarea></div>
        </div>
        <div class="field two" style="display: flex; align-items: end;">
          <button type="button" onclick="showItemsModal()" style="width: 100%; padding: 8px 12px; background: #3B82F6; color: white; border: none; border-radius: 4px; font-size: 12px; font-weight: 600; cursor: pointer;">Items Detail</button>
        </div>
        <div class="field full">
          <div class="label">Notes / Exceptions</div>
          <div class="value"><textarea id="notes_exceptions" placeholder="Any special notes or exceptions..."></textarea></div>
        </div>
      </div>
    </div>
        <div class="field third">
          <div class="label">Total Pieces</div>
          <div class="value"><input type="number" id="total_pieces" placeholder="25"></div>
        </div>
        <div class="field third">
          <div class="label">Ovens</div>
          <div class="value"><input type="number" id="ovens" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Atlas Box</div>
          <div class="value"><input type="number" id="atlas_box" placeholder="4"></div>
        </div>
        <div class="field third">
          <div class="label">Trolleys</div>
          <div class="value"><input type="number" id="trolleys" placeholder="2"></div>
        </div>
        <div class="field third">
          <div class="label">Waste Carts</div>
          <div class="value"><input type="number" id="waste_carts" placeholder="1"></div>
        </div>
        <div class="field third">
          <div class="label">Dry Ice (kg)</div>
          <div class="value"><input type="number" step="0.1" id="dry_ice_kg" placeholder="0.0"></div>
        </div>
        <div class="field third">
          <div class="label">Ice (kg)</div>
          <div class="value"><input type="number" step="0.1" id="ice_kg" placeholder="1.0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals Y</div>
          <div class="value"><input type="number" id="meals_y" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals P</div>
          <div class="value"><input type="number" id="meals_p" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals J</div>
          <div class="value"><input type="number" id="meals_j" placeholder="0"></div>
        </div>
        <div class="field third">
          <div class="label">Meals F</div>
          <div class="value"><input type="number" id="meals_f" placeholder="0"></div>
        </div>
        <div class="field half">
          <div class="label">Special Meals</div>
          <div class="value"><input type="text" id="special_meals" placeholder="Ej. VGML, KSML, etc."></div>
        </div>
        <div class="field half">
          <div class="label">Special Beverages</div>
          <div class="value"><input type="text" id="special_beverages" placeholder="Ej. Wine, Champagne, etc."></div>
        </div>
        <div class="field third">
          <div class="label">Special Instructions</div>
          <div class="value"><input type="text" id="special_instructions" placeholder="Ej. Keep refrigerated"></div>
        </div>
        <div class="field full">
          <div class="label">Notes / Exceptions</div>
          <div class="value"><textarea id="notes_exceptions" placeholder="Any special notes or exceptions..."></textarea></div>
        </div>
      </div>
    </div>
        <div class="field third">
          <div class="label">Total Pieces</div>
          <div class="value"><input type="number" id="total_pieces" placeholder="25"></div>
        </div>
        <div class="field third">
          <div class="label">Total Weight (kg)</div>
          <div class="value"><input type="number" id="total_weight" placeholder="150.5"></div>
        </div>
        <div class="field third">
          <div class="label">Special Instructions</div>
          <div class="value"><input type="text" id="special_instructions" placeholder="Ej. Keep refrigerated"></div>
        </div>
      </div>
    </div>

    <!-- Notes and Comments -->
    <div class="card" style="grid-column: span 12;">
      <h3>Notes and Comments</h3>
      <div class="row">
        <div class="field full">
          <div class="label">Delivery Notes</div>
          <div class="value"><textarea id="delivery_notes" placeholder="Any delivery notes or issues..."></textarea></div>
        </div>
        <div class="field full">
          <div class="label">Quality Check Notes</div>
          <div class="value"><textarea id="quality_notes" placeholder="Quality inspection notes..."></textarea></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Signatures -->
  <div class="signatures">
    <div class="signature-box">
      <div class="signature-title">Driver Signature</div>
      <div class="signature-line"></div>
      <div style="font-size: 12px; color: #6B7280;">
        <div>Name: <input type="text" id="driver_sig_name" style="border:none; border-bottom:1px solid #ccc; width:200px;" placeholder="Driver Name"></div>
        <div style="margin-top:8px;">Date: <input type="date" id="driver_sig_date" style="border:none; border-bottom:1px solid #ccc; width:120px;"></div>
      </div>
    </div>
    <div class="signature-box">
      <div class="signature-title">Receiver Signature</div>
      <div class="signature-line"></div>
      <div style="font-size: 12px; color: #6B7280;">
        <div>Name: <input type="text" id="receiver_sig_name" style="border:none; border-bottom:1px solid #ccc; width:200px;" placeholder="Receiver Name"></div>
        <div style="margin-top:8px;">Date: <input type="date" id="receiver_sig_date" style="border:none; border-bottom:1px solid #ccc; width:120px;"></div>
      </div>
    </div>
  </div>
  <div class="section no-print" style="margin-top: 16px;">
    <button onclick="saveAsPDF()" style="padding:8px 12px; border:1px solid #D1D5DB; border-radius:6px; background:#111827; color:#fff; cursor:pointer;">Save</button>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"></script>
  <script>
    // Generate barcode and QR code
    function generateCodes() {
      const shipmentId = document.getElementById('otm_shipment_id').value || 'OTM-123456';
      
      // Generate barcode
      JsBarcode("#barcode", shipmentId, {
        format: "CODE128",
        width: 1,
        height: 30,
        displayValue: true,
        fontSize: 10
      });
      
      // Generate QR code
      const qrData = JSON.stringify({
        shipment_id: shipmentId,
        delivery_slip: document.getElementById('delivery_slip_number').value || 'DS-0001',
        flight: document.getElementById('flight_number').value || 'SA123',
        date: new Date().toISOString().split('T')[0]
      });
      
      QRCode.toCanvas(document.createElement('canvas'), qrData, {width: 80}, function (error, canvas) {
        if (!error) {
          document.getElementById('qrcode').innerHTML = '';
          document.getElementById('qrcode').appendChild(canvas);
        }
      });
    }
    
    // Save as PDF function
    function saveAsPDF() {
      // Update codes before saving
      generateCodes();
      
      // Hide the save button
      document.querySelector('.no-print').style.display = 'none';
      
      // Use browser print to PDF
      window.print();
      
      // Show button again
      setTimeout(() => {
        document.querySelector('.no-print').style.display = 'block';
      }, 1000);
    }
    
    // Generate codes when page loads and when key fields change
    document.addEventListener('DOMContentLoaded', generateCodes);
    document.getElementById('otm_shipment_id').addEventListener('input', generateCodes);
    document.getElementById('delivery_slip_number').addEventListener('input', generateCodes);
    document.getElementById('flight_number').addEventListener('input', generateCodes);
  </script>

    <!-- Items Detail Modal -->
    <div id="itemsModal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);">
        <div style="background-color: white; margin: 2% auto; padding: 0; border-radius: 8px; width: 90%; max-width: 1200px; max-height: 90vh; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            <div style="background: #3B82F6; color: white; padding: 16px; display: flex; justify-content: space-between; align-items: center;">
                <h2 style="margin: 0; font-size: 18px; font-weight: 600;">Available Catering Items</h2>
                <span onclick="closeItemsModal()" style="color: white; font-size: 24px; font-weight: bold; cursor: pointer; line-height: 1;">&times;</span>
            </div>
            <div style="padding: 16px; max-height: calc(90vh - 140px); overflow-y: auto;">
                <div id="itemsContent" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;"></div>
            </div>
            <div style="padding: 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; text-align: center;">
                <button onclick="addSelectedItems()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; margin: 0 4px; font-size: 12px;">Add Selected Items</button>
                <button onclick="selectAllItems()" style="padding: 8px 16px; background: #3B82F6; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; margin: 0 4px; font-size: 12px;">Select All</button>
                <button onclick="clearAllItems()" style="padding: 8px 16px; background: #6B7280; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; margin: 0 4px; font-size: 12px;">Clear All</button>
                <button onclick="closeItemsModal()" style="padding: 8px 16px; background: #6B7280; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; margin: 0 4px; font-size: 12px;">Cancel</button>
            </div>
        </div>
    </div>
    
    
    
    
    <script>
        // Items data from CSV with actual expected quantities
        const itemsData = {"Licores": ["JACK AND COKE", "TEQUILA 7 LEGUAS BLANCO", "TEQUILA 7 LEGUAS REPOSADO", "TEQUILA 7 LEGUAS AÑEJO", "RREY KOLSCH 273ML", "RREY LONDON 273ML", "COLIMITA", "CAYACO", "VINO BLANCO CRIA CUERVOS", "VINO TINTO CRIA CUERVOS", "AMSTEL ULTRA", "HEINEKEN ORIGINAL", "XX LAGER", "TECATE LIGHT", "TECATE ROJA 355 ML", "SOL CLAMATO", "INDIO", "RON BACARDI", "VODKA TITOS", "JACK DANIELS 50ML", "CORAJILLO", "CORAJILLO BAILEYS", "VINO TINTO SCIELO MX 187", "VINO ROSADO SCIELO MX 187"], "Lacteos": ["LECHE DE CHOCOLATE SC", "LECHE DE FRESA SC"], "Bebidas Calientes": ["CAPPUCHINO ORIGINAL", "CAPPUCHINO MOKA", "TE MANZANILLA JENGIBRE", "TE FRUTOS ROJOS", "CAFE COSTA"], "Botanas": ["NISHIKAWA JAPONES", "NISHIKAWA SALADO", "NUTTY BERRY MIX", "LUXURY NUT MIX", "SALSA BOTANERA", "CHIPS JICAMA ENCHILADA", "CHIPS PLATANO NATURAL", "ARANDANO MANGO MIX", "FRUTOS SECOS ENCHILADOS", "DORITOS NACHO", "RUFFLES QUESO", "SABRITAS ORIGINALES", "FRITOS LIMON Y SAL", "CHEETOS", "CHURRUMAIS", "SABRITAS FLAMIN HOT", "CHEETOS FLAMIN HOT", "ATE CON CHILE", "NUEZ CARAMELO", "CARNE SECA ORIGINAL", "CARNE SECA HABANERO", "VEGGIE CHIPS CHIPOTLE", "VEGGIE SAL HIMALAYA"], "Refrescos": ["WAYU FLOR DE JAMAICA", "WAYU BLUEBERRY", "COCA SIN AZUCAR", "AGUA NATURAL 600 ML", "CIEL MINERALIZADA", "JUGO DE MANZANA", "JUGO DE MANGO", "COCA COLA DIETA", "COCA COLA REGULAR", "FRESCA", "SIDRAL MUNDET", "SPRITE", "FANTA DE NARANJA"], "Sopas": ["CHICHARAMEN PICANTE", "CHICHARAMEN CLASICO", "NISSIN PICANTE", "NISSIN DARK DRAGON", "NISSIN RES"], "Galletas": ["EMPERADOR CHOCOLATE", "QUAKER AVENA FRUTOS ROJOS", "CHOKIS", "ARCOIRIS", "MUFFIN CHOCOLATE"], "Perecederos": ["CUERNO CLASICO DE PAVO", "PANINI CLASICO", "PANINI INTEGRAL"], "Extras": ["HIELO 1KG"], "VIVA PLAY": ["VIVAPLAY"]};
        
        // Actual expected quantities by item name from CSV
        const itemQuantities = {"JACK AND COKE": 4, "LECHE DE CHOCOLATE SC": 4, "LECHE DE FRESA SC": 4, "CAPPUCHINO ORIGINAL": 7, "CAPPUCHINO MOKA": 3, "TEQUILA 7 LEGUAS BLANCO": 4, "TEQUILA 7 LEGUAS REPOSADO": 2, "TEQUILA 7 LEGUAS AÑEJO": 2, "NISHIKAWA JAPONES": 8, "NISHIKAWA SALADO": 8, "TE MANZANILLA JENGIBRE": 6, "TE FRUTOS ROJOS": 4, "NUTTY BERRY MIX": 4, "LUXURY NUT MIX": 4, "SALSA BOTANERA": 90, "RREY KOLSCH 273ML": 4, "RREY LONDON 273ML": 4, "WAYU FLOR DE JAMAICA": 8, "WAYU BLUEBERRY": 8, "COLIMITA": 6, "CAYACO": 6, "CHIPS JICAMA ENCHILADA": 7, "CHIPS PLATANO NATURAL": 7, "CHICHARAMEN PICANTE": 10, "CHICHARAMEN CLASICO": 6, "VINO BLANCO CRIA CUERVOS": 1, "VINO TINTO CRIA CUERVOS": 2, "ARANDANO MANGO MIX": 4, "FRUTOS SECOS ENCHILADOS": 4, "COCA SIN AZUCAR": 29, "AGUA NATURAL 600 ML": 70, "CIEL MINERALIZADA": 10, "JUGO DE MANZANA": 12, "JUGO DE MANGO": 12, "COCA COLA DIETA": 12, "COCA COLA REGULAR": 65, "FRESCA": 10, "SIDRAL MUNDET": 8, "SPRITE": 18, "FANTA DE NARANJA": 8, "CAFE COSTA": 40, "DORITOS NACHO": 28, "EMPERADOR CHOCOLATE": 8, "RUFFLES QUESO": 26, "SABRITAS ORIGINALES": 36, "QUAKER AVENA FRUTOS ROJOS": 8, "CHOKIS": 12, "FRITOS LIMON Y SAL": 28, "ARCOIRIS": 8, "CHEETOS": 8, "CHURRUMAIS": 8, "SABRITAS FLAMIN HOT": 18, "CHEETOS FLAMIN HOT": 18, "NISSIN PICANTE": 14, "NISSIN DARK DRAGON": 11, "NISSIN RES": 6, "AMSTEL ULTRA": 8, "HEINEKEN ORIGINAL": 6, "XX LAGER": 6, "TECATE LIGHT": 18, "TECATE ROJA 355 ML": 6, "SOL CLAMATO": 6, "INDIO": 10, "RON BACARDI": 3, "VODKA TITOS": 2, "JACK DANIELS 50ML": 4, "CORAJILLO": 2, "CORAJILLO BAILEYS": 1, "ATE CON CHILE": 8, "NUEZ CARAMELO": 8, "VINO TINTO SCIELO MX 187": 2, "VINO ROSADO SCIELO MX 187": 2, "CARNE SECA ORIGINAL": 4, "CARNE SECA HABANERO": 4, "VEGGIE CHIPS CHIPOTLE": 7, "VEGGIE SAL HIMALAYA": 7, "CUERNO CLASICO DE PAVO": 0, "MUFFIN CHOCOLATE": 0, "PANINI CLASICO": 0, "PANINI INTEGRAL": 0, "HIELO 1KG": 0, "VIVAPLAY": 3};
        
        function showItemsModal() {
            const modal = document.getElementById('itemsModal');
            const content = document.getElementById('itemsContent');
            
            let html = '';
            for (const [category, items] of Object.entries(itemsData)) {
                html += `<div style="border: 1px solid #E5E7EB; border-radius: 6px; padding: 12px; background: #F9FAFB;">
                    <h3 style="margin: 0 0 8px 0; color: #111827; font-size: 14px; font-weight: 600; border-bottom: 2px solid #3B82F6; padding-bottom: 4px;">${category} (${items.length} items)</h3>
                    <div style="max-height: 200px; overflow-y: auto;">`;
                
                items.forEach((item, index) => {
                    const itemId = `${category}_${index}`;
                    const expectedQty = itemQuantities[item] || 1;
                    html += `<div style="display: flex; align-items: center; padding: 4px 6px; margin: 1px 0; background: white; border-radius: 3px; font-size: 11px;">
                        <input type="checkbox" id="${itemId}" value="${item}" style="margin-right: 6px;" onchange="toggleQuantityControls('${itemId}')">
                        <label for="${itemId}" style="cursor: pointer; flex: 1; margin-right: 8px;">${item}</label>
                        <span style="color: #6B7280; font-size: 10px; margin-right: 8px; min-width: 40px; text-align: center; background: #F3F4F6; padding: 2px 4px; border-radius: 2px;">Exp: ${expectedQty}</span>
                        <div id="qty_${itemId}" style="display: none; align-items: center; gap: 4px;">
                            <button type="button" onclick="changeQuantity('${itemId}', -1)" style="width: 20px; height: 20px; border: 1px solid #D1D5DB; background: #F9FAFB; border-radius: 3px; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;">-</button>
                            <input type="number" id="input_${itemId}" value="${expectedQty}" min="0" style="width: 40px; height: 20px; border: 1px solid #D1D5DB; border-radius: 3px; text-align: center; font-size: 11px;">
                            <button type="button" onclick="changeQuantity('${itemId}', 1)" style="width: 20px; height: 20px; border: 1px solid #D1D5DB; background: #F9FAFB; border-radius: 3px; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;">+</button>
                        </div>
                    </div>`;
                });
                
                html += '</div></div>';
            }
            
            content.innerHTML = html;
            modal.style.display = 'block';
        }
        
        function toggleQuantityControls(itemId) {
            const checkbox = document.getElementById(itemId);
            const qtyControls = document.getElementById('qty_' + itemId);
            
            if (checkbox.checked) {
                qtyControls.style.display = 'flex';
            } else {
                qtyControls.style.display = 'none';
            }
        }
        
        function changeQuantity(itemId, change) {
            const input = document.getElementById('input_' + itemId);
            let currentValue = parseInt(input.value) || 0;
            let newValue = currentValue + change;
            
            if (newValue < 0) newValue = 0;
            input.value = newValue;
        }
        
        function closeItemsModal() {
            document.getElementById('itemsModal').style.display = 'none';
        }
        
        function addSelectedItems() {
            const checkboxes = document.querySelectorAll('#itemsContent input[type="checkbox"]:checked');
            const selectedItems = [];
            
            checkboxes.forEach(cb => {
                const itemId = cb.id;
                const quantityInput = document.getElementById('input_' + itemId);
                const quantity = quantityInput ? quantityInput.value : '1';
                const expectedQty = itemQuantities[cb.value] || 1;
                if (quantity > 0) {
                    selectedItems.push(`${quantity}x ${cb.value} (Expected: ${expectedQty})`);
                }
            });
            
            if (selectedItems.length > 0) {
                const itemsDetail = document.getElementById('items_detail');
                const currentText = itemsDetail.value.trim();
                const newText = selectedItems.join('\n');
                
                if (currentText) {
                    itemsDetail.value = currentText + '\n' + newText;
                } else {
                    itemsDetail.value = newText;
                }
            }
            
            closeItemsModal();
        }
        
        function selectAllItems() {
            const checkboxes = document.querySelectorAll('#itemsContent input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.checked = true;
                toggleQuantityControls(cb.id);
            });
        }
        
        function clearAllItems() {
            const checkboxes = document.querySelectorAll('#itemsContent input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.checked = false;
                toggleQuantityControls(cb.id);
            });
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('itemsModal');
            if (event.target === modal) {
                closeItemsModal();
            }
        }
    </script></body>
</html>
