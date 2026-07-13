// ======================================================
// INDODAX AI BOT
// dashboard.js V4 Full Replacement
// No dependency on api.js
// ======================================================

async function getJSON(url) {
    try {
        const res = await fetch(url + "?t=" + Date.now(), {
            cache: "no-store",
            headers: {
                "Accept": "application/json"
            }
        });

        if (!res.ok) throw new Error(res.status);

        return await res.json();

    } catch (e) {
        console.log("Fetch Error:", url, e);
        return null;
    }
}

function el(id) {
    return document.getElementById(id);
}

function setText(id, value) {
    const obj = el(id);
    if (obj) obj.innerText = value;
}

function formatIDR(v) {
    if (v == null) return "0";

    return "Rp " + Number(v).toLocaleString("id-ID");
}

async function refreshDashboard() {

    const status = await getJSON("/api/status");
    const stats = await getJSON("/api/stats");
    const positions = await getJSON("/api/positions");

    // ===============================
    // STATUS
    // ===============================

    if (status) {

        setText("bot-status",
            status.bot || "RUNNING"
        );

        setText("exchange-status",
            status.exchange || "-"
        );

        setText("btc-status",
            status.btc_status || "-"
        );

        setText("top-scanner",
            status.top_scanner || "-"
        );

        if (el("idr-balance"))
            el("idr-balance").innerText =
                formatIDR(status.idr_balance || 0);

        if (el("total-asset"))
            el("total-asset").innerText =
                formatIDR(status.total_asset || 0);

        if (el("recent-activity"))
            el("recent-activity").innerHTML =
                status.last_activity || "Belum ada aktivitas.";
    }

    // ===============================
    // STATS
    // ===============================

    if (stats) {

        setText("today-profit",
            (stats.today_profit || 0) + "%");

        setText("win-rate",
            (stats.winrate || 0) + "%");

    }

    // ===============================
    // ACTIVE POSITION
    // ===============================

    if (el("active-position")) {

        if (!positions || positions.length === 0) {

            el("active-position").innerHTML =
                "Belum ada posisi aktif.";

        } else {

            let html = "";

            positions.forEach(p => {

                html += `
                <div class="card" style="margin-bottom:10px">

                    <b>${p.symbol}</b><br>

                    Layer : ${p.layer ?? 1}<br>

                    Buy : ${p.buy_price ?? "-"}<br>

                    Profit :
                    ${p.profit_percent ?? 0}%<br>

                    Hold :
                    ${p.hold_time ?? "-"}

                </div>
                `;

            });

            el("active-position").innerHTML = html;

        }

    }

}

// =======================================
// AUTO REFRESH
// =======================================

document.addEventListener("DOMContentLoaded", () => {

    refreshDashboard();

    setInterval(refreshDashboard, 5000);

});
