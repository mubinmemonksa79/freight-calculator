import streamlit as st
import pandas as pd
from weasyprint import HTML
import io
import base64

st.set_page_config(page_title="Air Freight Calculator", layout="wide")

# Helper function to encode the logo safely
def get_base64_logo(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except:
        return None

# --- 1. LOGO SECTION ---
logo_b64 = get_base64_logo("logo.png")
if logo_b64:
    st.sidebar.image("logo.png", width=150)
else:
    st.sidebar.info("💡 Place 'logo.png' in the FreightTool folder to see it here.")

st.title("✈️ Air Freight Live Calculator")

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("Rates & Detailed Fees")
air_rate = st.sidebar.number_input("Air Rate (per KG)", value=7.00)
st.sidebar.markdown("---")
st.sidebar.subheader("Local Charges")
apt_transfer = st.sidebar.number_input("Air Port Transfer", value=60.0)
courier_chg = st.sidebar.number_input("Courier Charges", value=25.0)
misc_chg = st.sidebar.number_input("Misc Charges", value=100.0)
port_receipt = st.sidebar.number_input("Port Receipt Charges", value=100.0)
land_freight = st.sidebar.number_input("Land Freight", value=600.0)
aes_fee = st.sidebar.number_input("AES Fee", value=60.0)
doc_fee = st.sidebar.number_input("Documentation", value=50.0)

# --- 3. SHIPMENT DETAILS ---
st.header("Shipment Details")
df_init = pd.DataFrame([{"Pkgs": 1, "Length (cm)": 102, "Width (cm)": 120, "Height (cm)": 130, "Gross WT (per pkg)": 300}])
edited_df = st.data_editor(df_init, num_rows="dynamic", use_container_width=True)

# Calculation Logic
total_pkgs, total_vol_wt, total_gross_wt, rows_html = 0, 0.0, 0.0, ""
for _, row in edited_df.iterrows():
    if pd.notnull(row["Length (cm)"]) and pd.notnull(row["Pkgs"]):
        v_wt = (row["Length (cm)"] * row["Width (cm)"] * row["Height (cm)"] / 6000) * row["Pkgs"]
        g_wt = row["Gross WT (per pkg)"] * row["Pkgs"]
        total_pkgs += int(row["Pkgs"])
        total_vol_wt += v_wt
        total_gross_wt += g_wt
        rows_html += f"<tr><td>{row['Pkgs']}</td><td>{row['Length (cm)']}x{row['Width (cm)']}x{row['Height (cm)']}</td><td>{v_wt:.2f}</td><td>{g_wt:.2f}</td></tr>"

chargeable_wt = max(total_vol_wt, total_gross_wt)
pure_air_freight = chargeable_wt * air_rate
total_local_fees = apt_transfer + courier_chg + misc_chg + port_receipt + land_freight + aes_fee + doc_fee
grand_total = pure_air_freight + total_local_fees

# --- 4. SUMMARY SECTION ---
st.divider()
st.header("Shipment & Financial Summary")
s1, s2, s3, s4 = st.columns(4)
s1.metric("Total Pkgs", f"{total_pkgs}")
s2.metric("Total Vol WT", f"{total_vol_wt:.2f} KG")
s3.metric("Total Gross WT", f"{total_gross_wt:.2f} KG")
s4.metric("Chargeable WT", f"{chargeable_wt:.2f} KG")

c1, c2, c3 = st.columns(3)
c1.metric("Air Freight Cost", f"${pure_air_freight:.2f}")
c2.metric("Total Local Fees", f"${total_local_fees:.2f}")
c3.metric("GRAND TOTAL", f"${grand_total:.2f} USD")

st.header("Terms & Conditions")
terms = st.text_area("Enter your terms:", value="Quote valid for 7 days. Subject to space and equipment availability.")

# --- 5. PDF GENERATION ---
if st.button("Prepare PDF"):
    logo_html = f'<div style="max-height: 100px;"><img src="data:image/png;base64,{logo_b64}" style="max-height: 80px; width: auto;"></div>' if logo_b64 else ""
    
    html_string = f"""
    <html><head><style>
        body {{ font-family: Arial, sans-serif; padding: 30px; color: #333; line-height: 1.4; }}
        .header-table {{ width: 100%; border: none; margin-bottom: 30px; }}
        .header-table td {{ border: none; vertical-align: middle; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; font-size: 12px; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .summary-wrapper {{ margin-top: 20px; }}
        .summary-table {{ width: 450px; }}
        .grand-total {{ background-color: #eafaf1; font-weight: bold; font-size: 14px; color: #27ae60; }}
        .section-title {{ background-color: #eee; font-weight: bold; color: #444; }}
        .page-break {{ page-break-before: always; }}
        .terms-box {{ margin-top: 40px; padding: 15px; border: 1px solid #eee; background: #fafafa; }}
    </style></head><body>
        
        <table class="header-table">
            <tr>
                <td style="width: 50%;">{logo_html}</td>
                <td style="width: 50%; text-align: right;">
                    <h1 style="margin: 0; color: #2c3e50;">Air Freight Quotation</h1>
                </td>
            </tr>
        </table>

        <h3>1. Financial Summary</h3>
        <div class="summary-wrapper">
            <table class="summary-table">
                <tr class="section-title"><td colspan="2">Freight Details</td></tr>
                <tr><td>Chargeable Weight</td><td>{chargeable_wt:.2f} KG</td></tr>
                <tr><td>Air Freight Cost (@ ${air_rate}/kg)</td><td>${pure_air_freight:.2f}</td></tr>
                
                <tr class="section-title"><td colspan="2">Local Charges Breakdown</td></tr>
                <tr><td>Air Port Transfer</td><td>${apt_transfer:.2f}</td></tr>
                <tr><td>Courier Charges</td><td>${courier_chg:.2f}</td></tr>
                <tr><td>Misc Charges</td><td>${misc_chg:.2f}</td></tr>
                <tr><td>Port Receipt Charges</td><td>${port_receipt:.2f}</td></tr>
                <tr><td>Land Freight</td><td>${land_freight:.2f}</td></tr>
                <tr><td>AES Fee</td><td>${aes_fee:.2f}</td></tr>
                <tr><td>Documentation</td><td>${doc_fee:.2f}</td></tr>
                
                <tr class="grand-total"><td>GRAND TOTAL (USD)</td><td>${grand_total:.2f}</td></tr>
            </table>
        </div>

        <div class="page-break"></div>

        <table class="header-table">
            <tr>
                <td style="width: 50%;">{logo_html}</td>
                <td style="width: 50%; text-align: right;">
                    <h1 style="margin: 0; color: #2c3e50;">Shipment Specifications</h1>
                </td>
            </tr>
        </table>

        <h3>2. Shipment Dimensions</h3>
        <table>
            <tr><th>Pkgs</th><th>Dims (cm)</th><th>Vol WT (KG)</th><th>Gross WT (KG)</th></tr>
            {rows_html}
            <tr style="font-weight:bold;"><td>{total_pkgs}</td><td>TOTALS</td><td>{total_vol_wt:.2f}</td><td>{total_gross_wt:.2f}</td></tr>
        </table>

        <div class="terms-box">
            <strong>Terms & Conditions:</strong><br>
            <p style="white-space: pre-wrap; font-size: 11px;">{terms}</p>
        </div>
    </body></html>"""
    
    pdf_out = io.BytesIO()
    HTML(string=html_string).write_pdf(pdf_out)
    st.download_button(label="📩 Download Final Detailed PDF", data=pdf_out.getvalue(), file_name="Air_Freight_Quote.pdf", mime="application/pdf")
