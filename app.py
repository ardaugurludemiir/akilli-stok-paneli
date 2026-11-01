<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartStock Enterprise — Stochastic Decision Support System</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0f172a;
            --accent: #3b82f6;
            --bg-light: #f8fafc;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        body {
            background-color: #ffffff;
            color: var(--text-main);
            overflow-x: hidden;
            line-height: 1.6;
        }
        /* Navbar */
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 80px;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            z-index: 1000;
        }
        .logo {
            font-weight: 800;
            font-size: 1.4rem;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .nav-links {
            display: flex;
            gap: 30px;
            list-style: none;
            color: var(--text-muted);
            font-weight: 600;
            font-size: 0.95rem;
        }
        .nav-links a {
            text-decoration: none;
            color: inherit;
            transition: 0.3s;
        }
        .nav-links a:hover {
            color: var(--accent);
        }
        .nav-right {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .cta-btn {
            background: var(--primary);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: 0.3s;
            cursor: pointer;
            border: none;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        }
        .cta-btn:hover {
            background: var(--accent);
            transform: translateY(-2px);
        }
        .btn-outline {
            background: transparent;
            color: var(--primary);
            border: 2px solid var(--border-color);
        }
        .btn-outline:hover {
            border-color: var(--primary);
            background: transparent;
            color: var(--primary);
        }

        /* Hero Section */
        .hero {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 90px 20px 60px 20px;
            background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.1) 0%, transparent 60%);
        }
        .badge {
            background: #eff6ff;
            color: var(--accent);
            padding: 8px 18px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 25px;
            border: 1px solid #dbeafe;
        }
        .hero h1 {
            font-size: 3.8rem;
            font-weight: 900;
            line-height: 1.15;
            max-width: 950px;
            margin-bottom: 25px;
            color: var(--primary);
            letter-spacing: -1px;
        }
        .hero p {
            font-size: 1.2rem;
            color: var(--text-muted);
            max-width: 800px;
            line-height: 1.7;
            margin-bottom: 40px;
        }

        /* Features / Modules Section */
        .features-section {
            padding: 80px 80px;
            background: var(--bg-light);
        }
        .section-header {
            text-align: center;
            max-width: 700px;
            margin: 0 auto 50px auto;
        }
        .section-header h2 {
            font-size: 2.3rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 15px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: white;
            padding: 35px;
            border-radius: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border-color);
            transition: 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            border-color: var(--accent);
        }
        .card h3 {
            font-size: 1.25rem;
            color: var(--primary);
            margin-bottom: 12px;
            font-weight: 700;
        }
        .card p {
            color: var(--text-muted);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Modal (Kayıt / Giriş Penceresi) */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(5px);
            z-index: 2000;
            justify-content: center;
            align-items: center;
        }
        .modal-card {
            background: white;
            padding: 40px;
            border-radius: 24px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            position: relative;
            animation: modalFadeIn 0.3s ease;
        }
        @keyframes modalFadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .modal-close {
            position: absolute;
            top: 20px;
            right: 20px;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-muted);
        }
        .modal-card h2 {
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 10px;
        }
        .modal-card p {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 25px;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 8px;
            color: var(--primary);
        }
        .form-group input {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            font-size: 1rem;
            outline: none;
            transition: 0.3s;
        }
        .form-group input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        }
        .submit-btn {
            width: 100%;
            background: var(--primary);
            color: white;
            padding: 14px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            border: none;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 10px;
        }
        .submit-btn:hover {
            background: var(--accent);
        }

        /* Footer */
        footer {
            text-align: center;
            padding: 40px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.95rem;
            background: #ffffff;
        }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav>
        <div class="logo">📦 SmartStock Enterprise</div>
        <ul class="nav-links">
            <li><a href="#features">Core Features</a></li>
        </ul>
        <div class="nav-right">
            <button class="cta-btn btn-outline" onclick="openModal()">Oturum Aç</button>
            <button class="cta-btn" onclick="openModal()">Hemen Kaydol</button>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="badge">⚡ Industrial Engineering Decision Support System</div>
        <h1>Stochastic Intelligence.<br>Absolute Inventory Control.</h1>
        <p>An enterprise-grade platform engineered to eliminate stockout vulnerabilities, optimize probabilistic safety thresholds, and synchronize macroeconomic currency fluctuations (USD/TRY) with real-time warehouse execution.</p>
        <button class="cta-btn" style="padding: 16px 36px; font-size: 1.1rem;" onclick="openModal()">Platformu Keşfet & Başla</button>
    </section>

    <!-- Features Section -->
    <section class="features-section" id="features">
        <div class="section-header">
            <h2>Kritik Karar Destek Modülleri</h2>
            <p>Endüstriyel gereksinimlere tam uygun, stokastik ve makroekonomik altyapı.</p>
        </div>
        <div class="grid">
            <div class="card">
                <h3>💱 Canlı Döviz Entegrasyonu (USD/TRY)</h3>
                <p>Küresel API kaynaklarından anlık döviz kurlarını çekerek portföy değerlemelerini ve sermaye bütçelemesini dinamik olarak Türk Lirası veya Amerikan Doları cinsinden senkronize eder.</p>
            </div>
            <div class="card">
                <h3>📊 ABC Pareto Analizi</h3>
                <p>Yıllık tüketim değeri etkisine göre envanter varlıklarını sınıflandırır, yüksek etkili stok kalemlerine operasyonel odaklanma sağlar.</p>
            </div>
            <div class="card">
                <h3>⚖️ Stokastik Talep ve Z-Skoru</h3>
                <p>Güvenlik stoğu ve yeniden sipariş noktalarını (ROP) %90 ila %99.9 hedef hizmet seviyelerine göre olasılıksal dağılımlarla hesaplar.</p>
            </div>
            <div class="card">
                <h3>🚨 Kapsamlı Risk Matrisi</h3>
                <p>Tüm operasyonel node'lar üzerinde kritik stok tükenme risklerini, aşırı sermaye kilitlenmelerini ve uyarı bölgelerini anlık olarak denetler.</p>
            </div>
            <div class="card">
                <h3>🏢 Multi-Echelon Depo Ağı</h3>
                <p>İstanbul, İzmir ve Adana gibi dağıtık depolama tesislerini ve yerel tedarik sürelerini eş zamanlı olarak koordine eder.</p>
            </div>
            <div class="card">
                <h3>💰 Çalışma Sermayesi Bütçelemesi</h3>
                <p>Kritik stok kalemlerini en uygun ROP seviyelerine getirmek için gereken tam sermaye tahsisatını likiditeyi koruyarak hesaplar.</p>
            </div>
        </div>
    </section>

    <!-- Kayıt / Giriş Modal -->
    <div class="modal-overlay" id="authModal">
        <div class="modal-card">
            <button class="modal-close" onclick="closeModal()">&times;</button>
            <h2>Platforma Katılın</h2>
            <p>E-posta ve telefon numaranızı girerek SmartStock karar destek sistemine anında erişim sağlayın.</p>
            
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label>E-posta Adresi</label>
                    <input type="email" id="userEmail" placeholder="ornek@sirket.com" required>
                </div>
                <div class="form-group">
                    <label>Telefon Numarası</label>
                    <input type="tel" id="userPhone" placeholder="0555 555 55 55" required>
                </div>
                <button type="submit" class="submit-btn">Sisteme Giriş Yap →</button>
            </form>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>© 2026 SmartStock Enterprise Decision Support Systems. All rights reserved.</p>
    </footer>

    <script>
        const modal = document.getElementById('authModal');

        function openModal() {
            modal.style.display = 'flex';
        }

        function closeModal() {
            modal.style.display = 'none';
        }

        function handleLogin(event) {
            event.preventDefault();
            const email = document.getElementById('userEmail').value;
            const phone = document.getElementById('userPhone').value;
            
            if(email && phone) {
                alert("Kayıt başarılı! Karar destek paneline yönlendiriliyorsunuz.");
                window.location.href = "https://smartstock-enterprise.streamlit.app"; 
            }
        }

        window.onclick = function(event) {
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
