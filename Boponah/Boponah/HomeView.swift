//
//  ContentView.swift
//  L1Demo
//
//  Created by Jacob Gino on 8/25/23.
//

import SwiftUI
import PythonKit


class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, open url: URL, sourceApplication: String?, annotation: Any) -> Bool {
        // Handle the URL that Spotify redirects to
        if url.scheme == "boponah" {
            // Process the URL
            print("Spotify URL: \(url)")
            // You can parse the URL and take appropriate actions
        }
        return true
    }
}

struct HomeView: View {
    @State private var email: String = ""
    @State private var password: String = ""

    var body: some View {
            ZStack {
                LinearGradient(gradient: Gradient(colors: [Color.blue.opacity(0.3), Color.white]),
                               startPoint: .topLeading,
                               endPoint: .bottomTrailing)
                    .edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 10) {
                    Image("Logo")
                        .resizable()
                        .frame(width: 240, height: 240)
                        .foregroundColor(.green)
                    
                    Text("Boponah")
                        .font(.system(size: 40, weight: .bold, design: .rounded))
                        .foregroundColor(.black)
                    
                    Button(action: {
                        openURL()
                    }) {
                        HStack {
                            Image("Spotify")
                                .resizable()
                                .frame(width: 20, height: 20)
                            
                            Text("Login with Spotify")
                                .font(.system(size: 20, weight: .medium, design: .rounded))
                        }
                        .padding()
                        .background(Color.black)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                        .shadow(color: .gray, radius: 5, x: 0, y: 5)
                    }
                }
             
            }
        }
    func openURL() {
            if let url = URL(string: "http://127.0.0.1:5001/login") {
                UIApplication.shared.open(url)
            }
    }
    
    func runPythonCode() {
            let sys = Python.import("sys")
            sys.path.append("../")

            let example = Python.import("test")
            if let result = example.get_data().string {
                DispatchQueue.main.async {
                    s
                }
      
            }
        }
}

struct HomeView_Previews: PreviewProvider {
    static var previews: some View {
        HomeView()
    }
}
