package com.lathapg.manager;

import android.annotation.SuppressLint;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.OnBackPressedCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends AppCompatActivity {

    private static final String PREF_NAME = "latha_pg_prefs";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String DEFAULT_URL = "http://10.0.2.2:8000/dashboard/";

    private WebView webView;
    private SwipeRefreshLayout swipeRefresh;
    private LinearLayout layoutError;
    private TextView tvErrorUrl;
    private ImageButton btnSettings;
    private SharedPreferences preferences;

    private ValueCallback<Uri[]> fileUploadCallback;
    private ActivityResultLauncher<Intent> fileChooserLauncher;
    private long backPressedTime = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        preferences = getSharedPreferences(PREF_NAME, MODE_PRIVATE);

        webView = findViewById(R.id.webView);
        swipeRefresh = findViewById(R.id.swipeRefresh);
        layoutError = findViewById(R.id.layoutError);
        tvErrorUrl = findViewById(R.id.tvErrorUrl);
        btnSettings = findViewById(R.id.btnSettings);

        initFileChooser();
        setupWebView();
        setupListeners();
        setupBackNavigation();

        loadCurrentServerUrl();
    }

    private void initFileChooser() {
        fileChooserLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (fileUploadCallback != null) {
                    Uri[] results = null;
                    if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                        if (result.getData().getClipData() != null) {
                            int count = result.getData().getClipData().getItemCount();
                            results = new Uri[count];
                            for (int i = 0; i < count; i++) {
                                results[i] = result.getData().getClipData().getItemAt(i).getUri();
                            }
                        } else if (result.getData().getData() != null) {
                            results = new Uri[]{result.getData().getData()};
                        }
                    }
                    fileUploadCallback.onReceiveValue(results);
                    fileUploadCallback = null;
                }
            }
        );
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                // Handle tel:, mailto:, and whatsapp: intents natively
                if (url.startsWith("tel:") || url.startsWith("mailto:") || url.startsWith("https://api.whatsapp.com") || url.startsWith("whatsapp://")) {
                    try {
                        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        startActivity(intent);
                        return true;
                    } catch (Exception e) {
                        Toast.makeText(MainActivity.this, "No app available to handle this action", Toast.LENGTH_SHORT).show();
                        return true;
                    }
                }
                return false;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                swipeRefresh.setRefreshing(false);
                layoutError.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                if (request.isForMainFrame()) {
                    swipeRefresh.setRefreshing(false);
                    webView.setVisibility(View.GONE);
                    layoutError.setVisibility(View.VISIBLE);
                    String currentUrl = preferences.getString(KEY_SERVER_URL, DEFAULT_URL);
                    tvErrorUrl.setText("Attempted URL: " + currentUrl);
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
                if (fileUploadCallback != null) {
                    fileUploadCallback.onReceiveValue(null);
                }
                fileUploadCallback = filePathCallback;

                Intent intent = fileChooserParams.createIntent();
                try {
                    fileChooserLauncher.launch(intent);
                } catch (Exception e) {
                    fileUploadCallback = null;
                    Toast.makeText(MainActivity.this, "Cannot open file chooser", Toast.LENGTH_SHORT).show();
                    return false;
                }
                return true;
            }
        });
    }

    private void setupListeners() {
        swipeRefresh.setOnRefreshListener(() -> webView.reload());

        btnSettings.setOnClickListener(v -> showServerSettingsDialog());

        findViewById(R.id.btnRetry).setOnClickListener(v -> {
            layoutError.setVisibility(View.GONE);
            webView.setVisibility(View.VISIBLE);
            swipeRefresh.setRefreshing(true);
            loadCurrentServerUrl();
        });

        findViewById(R.id.btnChangeUrl).setOnClickListener(v -> showServerSettingsDialog());
    }

    private void setupBackNavigation() {
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack();
                } else {
                    if (backPressedTime + 2000 > System.currentTimeMillis()) {
                        finish();
                    } else {
                        Toast.makeText(MainActivity.this, "Press back again to exit", Toast.LENGTH_SHORT).show();
                        backPressedTime = System.currentTimeMillis();
                    }
                }
            }
        });
    }

    private void loadCurrentServerUrl() {
        String url = preferences.getString(KEY_SERVER_URL, DEFAULT_URL);
        webView.loadUrl(url);
    }

    private void showServerSettingsDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(R.string.server_settings_title);

        LinearLayout container = new LinearLayout(this);
        container.setOrientation(LinearLayout.VERTICAL);
        container.setPadding(48, 24, 48, 12);

        TextView infoText = new TextView(this);
        infoText.setText("Enter your backend URL:\n• Cloudflare Tunnel (e.g. https://xxx.trycloudflare.com/dashboard/)\n• Local WiFi IP (e.g. http://192.168.1.10:8000/dashboard/)\n• Emulator (http://10.0.2.2:8000/dashboard/)");
        infoText.setTextSize(13f);
        infoText.setPadding(0, 0, 0, 16);
        container.addView(infoText);

        final EditText input = new EditText(this);
        String current = preferences.getString(KEY_SERVER_URL, DEFAULT_URL);
        input.setText(current);
        input.setSelection(input.getText().length());
        container.addView(input);

        builder.setView(container);

        builder.setPositiveButton(R.string.save, (dialog, which) -> {
            String newUrl = input.getText().toString().trim();
            if (!newUrl.isEmpty()) {
                if (!newUrl.startsWith("http://") && !newUrl.startsWith("https://")) {
                    newUrl = "http://" + newUrl;
                }
                if (!newUrl.endsWith("/")) {
                    newUrl = newUrl + "/";
                }
                if (!newUrl.contains("dashboard")) {
                    newUrl = newUrl + "dashboard/";
                }
                preferences.edit().putString(KEY_SERVER_URL, newUrl).apply();
                Toast.makeText(MainActivity.this, "Connecting to: " + newUrl, Toast.LENGTH_SHORT).show();
                layoutError.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);
                swipeRefresh.setRefreshing(true);
                webView.loadUrl(newUrl);
            }
        });

        builder.setNegativeButton(R.string.cancel, (dialog, which) -> dialog.cancel());
        builder.show();
    }
}
