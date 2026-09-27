"""
components/semaforo_widget.py
Componente customizado em JavaScript puro (Chart.js) para o "Termômetro"
visual do semáforo de crédito, embutido via streamlit.components.v1.html.

Este é o componente que atende ao requisito "Script web (JavaScript)" do
projeto: um gauge animado, desenhado no canvas com Chart.js, com uma
agulha (needle plugin escrito à mão) indicando o nível de alerta atual.
"""

from __future__ import annotations

CDN_CHARTJS = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"


def render_semaforo_gauge_html(pontos: int, nivel: str, titulo: str,
                                mensagem: str, cor_hex: str, max_pontos: int = 5) -> str:
    """
    Retorna um HTML autocontido (script + canvas) pronto para ser
    passado a st.components.v1.html().

    pontos: quantidade de sinais de alerta (0 a max_pontos)
    nivel: "verde" | "amarelo" | "vermelho"
    """
    pontos = max(0, min(pontos, max_pontos))
    angulo_agulha = -90 + (pontos / max_pontos) * 180  # -90 (verde) a +90 (vermelho)

    return f"""
<div style="font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;">
  <div role="img"
       aria-label="Semáforo de crédito: {titulo}. {mensagem}"
       style="max-width: 340px; margin: 0 auto;">
    <canvas id="gaugeCanvas" width="340" height="200"></canvas>
  </div>
  <div style="text-align:center; margin-top: -8px;">
    <div style="font-size: 1.15rem; font-weight: 700; color: {cor_hex};">{titulo}</div>
    <div style="font-size: 0.92rem; color: #333; margin-top: 4px; line-height:1.4;">{mensagem}</div>
  </div>
</div>

<script src="{CDN_CHARTJS}"></script>
<script>
(function() {{
  const ctx = document.getElementById('gaugeCanvas').getContext('2d');
  const targetAngle = {angulo_agulha};

  const needlePlugin = {{
    id: 'needle',
    afterDatasetDraw(chart) {{
      const {{ctx, chartArea: {{left, right, top, bottom}}}} = chart;
      const cx = (left + right) / 2;
      const cy = bottom - 4;
      const radius = Math.min(right - left, (bottom - top) * 2) / 2 - 10;

      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate((Math.PI / 180) * chart.needleAngle);
      ctx.beginPath();
      ctx.moveTo(0, 6);
      ctx.lineTo(radius * 0.78, 0);
      ctx.lineTo(0, -6);
      ctx.closePath();
      ctx.fillStyle = '#2b2b2b';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(0, 0, 8, 0, Math.PI * 2);
      ctx.fillStyle = '#2b2b2b';
      ctx.fill();
      ctx.restore();
    }}
  }};

  const chart = new Chart(ctx, {{
    type: 'doughnut',
    data: {{
      datasets: [{{
        data: [1, 1, 1],
        backgroundColor: ['#1E8E3E', '#F2A600', '#D93025'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270,
        cutout: '70%'
      }}]
    }},
    options: {{
      responsive: false,
      animation: {{ duration: 900, easing: 'easeOutQuart' }},
      plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
    }},
    plugins: [needlePlugin]
  }});

  // Anima a agulha do ângulo inicial (verde) até o ângulo alvo
  chart.needleAngle = -90;
  const start = performance.now();
  const duration = 900;
  function animateNeedle(now) {{
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    chart.needleAngle = -90 + eased * (targetAngle - (-90));
    chart.draw();
    if (t < 1) requestAnimationFrame(animateNeedle);
  }}
  requestAnimationFrame(animateNeedle);
}})();
</script>
"""
