from flask import Flask, request, render_template
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)
pio.templates.default = "plotly_white"

# --- Hàm tính diện tích mặt ướt ---
def calculate_S(method, L, B, d, delta, V):
    if method == "vantai":
        return L * d * (2 + 1.37 * (delta - 0.274) * B / d)
    elif method == "nhanh":
        return L * d * (1.36 + 1.37 * delta * B / d)
    elif method == "nho_nhanh":
        return 2.75 * np.sqrt(V * L)
    elif method == "muragin":
        return L * d * (1.36 + 1.13 * delta * B / d)
    elif method == "delta_lon":
        return L * (0.5 * B + d) * (0.55 + 1.52 * delta)
    elif method == "karpov":
        return np.cbrt(V ** 2) * (5.1 + 0.074 * L / d - 0.4 * delta)
    else:
        return 0

# --- Hàm tính sức cản ---
def calculate_R(S, L, B, delta, W, v):
    return 0.17 * S * v ** 1.825 + 1.45 * (24 - L / B) * delta ** 2.5 * (W / L**2) * v**4

# --- Dữ liệu để vẽ đồ thị ---
def generate_data(S, L, B, delta, W):
    v_values = np.linspace(1, 10, 100)
    R_values = [calculate_R(S, L, B, delta, W, v) for v in v_values]
    return v_values, R_values

# --- Tạo biểu đồ Plotly ---
def plot_chart(v_values, R_values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v_values, y=R_values, mode='lines+markers', name='R(v)'))
    fig.update_layout(title='Biểu đồ sức cản theo vận tốc',
                      xaxis_title='Vận tốc (m/s)',
                      yaxis_title='Sức cản (N)')
    return pio.to_html(fig, full_html=False)

# --- Trang chính ---
@app.route('/', methods=['GET', 'POST'])
def index():
    chart_html = ""
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            L = float(request.form['L'])
            B = float(request.form['B'])
            d = float(request.form['d'])
            delta = float(request.form['delta'])
            W = float(request.form['W'])
            V = float(request.form['V'])
            method = request.form['method']

            # Tính toán
            S = calculate_S(method, L, B, d, delta, V)
            v_vals, R_vals = generate_data(S, L, B, delta, W)
            chart_html = plot_chart(v_vals, R_vals)

        except Exception as e:
            chart_html = f"<p style='color:red;'>Lỗi: {str(e)}</p>"

    return render_template("index.html", chart_html=chart_html)

# --- Khởi chạy ---
if __name__ == '__main__':
    app.run(debug=True)
