import frida
import sys
import hashlib
import time
import re
import os
import subprocess
from xml.etree import ElementTree as ET
from Crypto.PublicKey import RSA

def get_installed_apps(device):
    pm_path = device.get_executable_path('pm')
    pm_output = device.spawn_output([pm_path, 'list', 'packages', '-f']).decode('utf-8')
    apps = [line.split('=', 1) for line in pm_output.strip().split('\n') if not line.startswith("package:/system")]
    return apps

def choose_target_app(apps):
    print("Select the target app:")
    for i, app in enumerate(apps, start=1):
        app_name = re.sub(r'\.apk$', '', app[0].split('/')[-1])
        print(f"{i}: {app_name} ({app[1]})")

    choice = -1
    while choice < 1 or choice > len(apps):
        try:
            choice = int(input("Enter the number of the target app: "))
        except ValueError:
            print("Invalid input, please enter a valid number.")
    return apps[choice - 1]

def order_id_generator(package_name):
    while True:
        unique_str = f"{package_name}_{time.time()}"
        order_id = hashlib.md5(unique_str.encode()).hexdigest()
        yield order_id

def bypass_ssl_pinning(package_name, device):
    jscode = """
    Java.perform(function() {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var TrustManagerImpl = Java.registerClass({
            name: 'com.example.TrustManagerImpl',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {},
                getAcceptedIssuers: function() {
                    return [];
                }
            }
        });

        var TrustManagers = Java.array('javax.net.ssl.TrustManager', [TrustManagerImpl.$new()]);
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
        var context = SSLContext.getInstance('TLS');
        context.init(null, TrustManagers, null);
        var defaultContext = SSLContext.getDefault();
        SSLContext.setDefault(context);
    });
    """
    session = device.attach(package_name)
    script = session.create_script(jscode)
    script.load()

def spoof_signature(package_name, device):
    private_key, public_key = generate_rsa_key_pair()

    jscode = """
    Java.perform(function() {
        var Context = Java.use('android.content.Context');
        var context = Context.getApplicationContext();
        var packageManager = context.getPackageManager();
        var packageInfo = packageManager.getPackageInfo('{package_name}', 64);

        var signatures = packageInfo.signatures;
        var signature = signatures[0];

        var signatureClass = Java.use('android.content.pm.Signature');
        var byteArrayInputStreamClass = Java.use('java.io.ByteArrayInputStream');
        var certificateFactoryClass = Java.use('java.security.cert.CertificateFactory');
        var x509CertificateClass = Java.use('java.security.cert.X509Certificate');
        var x509EncodedKeySpecClass = Java.use('java.security.spec.X509EncodedKeySpec');
        var keyFactoryClass = Java.use('java.security.KeyFactory');
        var keyStoreClass = Java.use('java.security.KeyStore');
        var privateKeyClass = Java.use('java.security.PrivateKey');
        var keyPairClass = Java.use('java.security.KeyPair');
        var keyPairGeneratorClass = Java.use('java.security.KeyPairGenerator');
        var signature Bytes = Java.use('java.security.Signature').$new('SHA256withRSA').sign(signature.toByteArray());
        var x509EncodedKeySpecClass = Java.use('java.security.spec.X509EncodedKeySpec');
        var keyFactoryClass = Java.use('java.security.KeyFactory');
        var keyPairClass = Java.use('java.security.KeyPair');
        var keyPairGeneratorClass = Java.use('java.security.KeyPairGenerator');
        var keyStoreClass = Java.use('java.security.KeyStore');
        var byteArrayInputStream = byteArrayInputStreamClass.$new(signature.toByteArray());
        var certificateFactory = certificateFactoryClass.getInstance('X.509');
        var certificate = certificateFactory.generateCertificate(byteArrayInputStream);
        byteArrayInputStream.close();

        var publicKey = certificate.getPublicKey();
        var encodedPublicKey = publicKey.getEncoded();
        var x509Certificate = x509CertificateClass.$new(encodedPublicKey);

        var encodedCertificate = x509Certificate.getEncoded();
        var x509EncodedKeySpec = x509EncodedKeySpecClass.$new(encodedCertificate);
        var keyFactory = keyFactoryClass.getInstance('RSA');
        var publicKeyObject = keyFactory.generatePublic(x509EncodedKeySpec);

        var privateKey = privateKeyClass.$new();
        var keyPair = keyPairClass.$new(publicKeyObject, privateKey);
        var keyPairGenerator = keyPairGeneratorClass.getInstance('RSA');
        var keyStore = keyStoreClass.getInstance('JKS');

        keyStore.load(null, null);
        keyStore.setKeyEntry('dummy', privateKey, null, [x509Certificate]);

        var keyStoreFileOutputStream = context.openFileOutput('keystore.jks', 0);
        keyStore.store(keyStoreFileOutputStream, 'password');
        keyStoreFileOutputStream.close();

        console.log('Signature spoofing completed.');
    });
    """.format(package_name=package_name)

    session = device.attach(package_name)
    script = session.create_script(jscode)
    script.load()

def generate_rsa_key_pair():
    key_pair = RSA.generate(2048)
    private_key = key_pair.export_key()
    public_key = key_pair.publickey().export_key()
    return private_key, public_key

def fill_custom_values(app_name, package_name, apk_file):
    decompiled_dir = os.path.splitext(apk_file)[0]
    os.makedirs(decompiled_dir, exist_ok=True)
    subprocess.run(["apktool", "d", "-f", apk_file, "-o", decompiled_dir], check=True)

    custom_values = generate_custom_values_from_apk(decompiled_dir)
    manipulate_local_storage(package_name, custom_values)

def generate_custom_values_from_apk(decompiled_dir):
    manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    package_name = root.attrib.get("package")
    
    custom_values = {}
    
    for element in root.iter():
        if 'android:name' in element.attrib and 'android:value' in element.attrib:
            key = element.attrib['android:name']
            value = element.attrib['android:value']
            custom_values[key] = value

    return custom_values

def manipulate_local_storage(package_name, custom_values):
    jscode = """
    Java.perform(function() {
        var Context = Java.use('android.content.Context');
        var sharedPreferences = Context.getSharedPreferences.call(Context, '{package_name}', 0);
        var editor = sharedPreferences.edit();
        
        // Set custom values
        {custom_values}

        editor.apply();
        console.log('Local storage manipulated.');
    });
    """.format(package_name=package_name, custom_values=custom_values)

    session = device.attach(package_name)
    script = session.create_script(jscode)
    script.load()

def main():
    device = frida.get_usb_device()

    apps = get_installed_apps(device)
    target_app = choose_target_app(apps)
    app_name = re.sub(r'\.apk$', '', target_app[0].split('/')[-1])
    package_name = target_app[1]

    order_id_gen = order_id_generator(package_name)
    order_id = next(order_id_gen)

    # Bypass SSL pinning
    bypass_ssl_pinning(package_name, device)

    # Generate custom values based on the chosen APK
    apk_file = f"{app_name}.apk"
    fill_custom_values(app_name, package_name, apk_file)

    # Spoof the signature
    spoof_signature(package_name, device)

    # Hook the BillingClient launchBillingFlow method
    jscode_template = """
    Java.perform(function() {
        var BillingClient = Java.use('com.android.billingclient.api.BillingClientImpl');

        BillingClient.launchBillingFlow.overload('android.app.Activity', 'com.android.billingclient.api.BillingFlowParams').implementation = function(activity, params) {
            console.log('[*] launchBillingFlow called');

            var isSubscription = params.zzhk() !== null;
            var response = {
                responseCode: 0,
                debugMessage: 'Generated result',
                purchasesList: [{
                    orderId: '{order_id}',
                    packageName: '{package_name}',
                    sku: params.getSku(),
                    purchaseTime: new Date().getTime(),
                    purchaseState: 0,
                    purchaseToken: 'generated_token',
                    isAutoRenewing: isSubscription
                }]
            };

            this.zzhc.value.onPurchasesUpdated(response.responseCode, response.purchasesList);

            return 0;
        };

        console.log('[*] BillingClient launchBillingFlow hooked');
    });
    """

    order_id_gen = order_id_generator(package_name)
    order_id = next(order_id_gen)

    jscode = jscode_template.format(package_name=package_name, order_id=order_id)

    session = device.attach(package_name)
    script = session.create_script(jscode)
    script.load()
    sys.stdin.read()

if __name__ == '__main__':
    main()
