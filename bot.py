<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔑 Keylogin API Test</title>
    <style>
        body {
            background: #1a1a1a;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #2d2d2d;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        
        h1 {
            text-align: center;
            color: #4CAF50;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        
        .test-item {
            background: #3a3a3a;
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #555;
        }
        
        .test-item.success {
            border-left-color: #4CAF50;
            background: #2a3a2a;
        }
        
        .test-item.error {
            border-left-color: #f44336;
            background: #3a2a2a;
        }
        
        .test-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #fff;
        }
        
        .test-result {
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        
        .status-success {
            color: #4CAF50;
            font-weight: bold;
        }
        
        .status-error {
            color: #f44336;
            font-weight: bold;
        }
        
        .summary {
            background: #333;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: center;
        }
        
        .summary h3 {
            color: #4CAF50;
            margin-top: 0;
        }
        
        pre {
            background: #222;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            color: #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔑 Keylogin API Test</h1>
        <p class="subtitle">API Sistem Testi</p>
        
        <?php
        $baseUrl = "https://midnightponywka.com";
        $adminToken = "ADMIN_API_SECRET_TOKEN_2024";
        $testKeys = ["59D6E83C6CCBD4B2", "C260970D9A9651CF"];
        
        $totalTests = 0;
        $passedTests = 0;
        
        // Test 1: API Stats
        echo '<div class="test-item" id="test1">';
        echo '<div class="test-title">📊 API İstatistikleri</div>';
        $response = @file_get_contents("$baseUrl/?api=1&token=$adminToken&action=stats");
        if ($response) {
            $data = json_decode($response, true);
            if ($data && $data['status'] === 'success') {
                echo '<div class="test-result status-success">✅ Başarılı</div>';
                echo '<div class="test-result">Toplam Key: ' . $data['total_keys'] . '</div>';
                echo '<div class="test-result">Version: ' . $data['version'] . '</div>';
                $passedTests++;
                echo '<script>document.getElementById("test1").classList.add("success");</script>';
            } else {
                echo '<div class="test-result status-error">❌ API yanıt verdi ama hata döndü</div>';
                echo '<script>document.getElementById("test1").classList.add("error");</script>';
            }
        } else {
            echo '<div class="test-result status-error">❌ API erişilemiyor</div>';
            echo '<script>document.getElementById("test1").classList.add("error");</script>';
        }
        echo '</div>';
        $totalTests++;
        
        // Test 2: Version
        echo '<div class="test-item" id="test2">';
        echo '<div class="test-title">🔧 Versiyon Kontrolü</div>';
        $response = @file_get_contents("$baseUrl/?api=1&token=$adminToken&action=version");
        if ($response) {
            $data = json_decode($response, true);
            if ($data && $data['status'] === 'success') {
                echo '<div class="test-result status-success">✅ Başarılı</div>';
                echo '<div class="test-result">Version: ' . $data['version'] . '</div>';
                $passedTests++;
                echo '<script>document.getElementById("test2").classList.add("success");</script>';
            } else {
                echo '<div class="test-result status-error">❌ Versiyon alınamadı</div>';
                echo '<script>document.getElementById("test2").classList.add("error");</script>';
            }
        } else {
            echo '<div class="test-result status-error">❌ Version API erişilemiyor</div>';
            echo '<script>document.getElementById("test2").classList.add("error");</script>';
        }
        echo '</div>';
        $totalTests++;
        
        // Test 3 & 4: Key Login Tests
        foreach ($testKeys as $index => $key) {
            $testNum = $index + 3;
            echo '<div class="test-item" id="test'.$testNum.'">';
            echo '<div class="test-title">🔑 Key Login Test #'.($index + 1).'</div>';
            echo '<div class="test-result">Key: ' . $key . '</div>';
            
            $postData = http_build_query(['key' => $key, 'sid' => 'TEST-SID-'.uniqid(), 'username' => 'TestUser']);
            $context = stream_context_create([
                'http' => [
                    'method' => 'POST',
                    'header' => 'Content-Type: application/x-www-form-urlencoded',
                    'content' => $postData
                ]
            ]);
            
            $response = @file_get_contents("$baseUrl/?api=1&token=$adminToken&action=key-login", false, $context);
            if ($response) {
                $data = json_decode($response, true);
                if ($data && ($data['status'] === 'success' || $data['authenticated'])) {
                    echo '<div class="test-result status-success">✅ Key geçerli</div>';
                    $passedTests++;
                    echo '<script>document.getElementById("test'.$testNum.'").classList.add("success");</script>';
                } else {
                    echo '<div class="test-result status-error">❌ ' . ($data['message'] ?? 'Key geçersiz') . '</div>';
                    echo '<script>document.getElementById("test'.$testNum.'").classList.add("error");</script>';
                }
            } else {
                echo '<div class="test-result status-error">❌ Key login API erişilemiyor</div>';
                echo '<script>document.getElementById("test'.$testNum.'").classList.add("error");</script>';
            }
            echo '</div>';
            $totalTests++;
        }
        
        // Summary
        echo '<div class="summary">';
        echo '<h3>Test Sonuçları</h3>';
        echo '<div class="test-result">Başarılı: <span class="status-success">' . $passedTests . '</span></div>';
        echo '<div class="test-result">Toplam: ' . $totalTests . '</div>';
        
        if ($passedTests === $totalTests) {
            echo '<div class="test-result status-success"><strong>✅ Tüm testler başarılı! C++ EXE çalışacaktır.</strong></div>';
        } else {
            echo '<div class="test-result status-error"><strong>❌ Bazı testler başarısız! API\'yi kontrol edin.</strong></div>';
        }
        echo '</div>';
        ?>
    </div>
</body>
</html> 
