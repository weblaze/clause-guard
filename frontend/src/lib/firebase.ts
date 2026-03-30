import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyCLvc9wKIMVv0c-4NUnONzI2OXwSGzVqck",
  authDomain: "clause-guard-cf894.firebaseapp.com",
  projectId: "clause-guard-cf894",
  storageBucket: "clause-guard-cf894.firebasestorage.app",
  messagingSenderId: "163518420439",
  appId: "1:163518420439:web:8a8f25615f6bf2877fe792"
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
