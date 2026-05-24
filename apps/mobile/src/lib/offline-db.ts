import { openDB, DBSchema } from "idb";

interface ConstructionEnterpriseOSOfflineDB extends DBSchema {
  "offline-reports": {
    key: string;
    value: {
      id: string;
      type: string;
      data: any;
      createdAt: string;
      synced: boolean;
    };
    indexes: { "by-synced": number };
  };
  "offline-photos": {
    key: string;
    value: {
      id: string;
      blob: Blob;
      metadata: any;
      createdAt: string;
      synced: boolean;
    };
    indexes: { "by-synced": number };
  };
  "cached-data": {
    key: string;
    value: { key: string; data: any; cachedAt: string; ttl: number };
  };
}

export async function getOfflineDB() {
  return openDB<ConstructionEnterpriseOSOfflineDB>(
    "construction-enterprise-os-offline",
    1,
    {
      upgrade(db) {
        const reportsStore = db.createObjectStore("offline-reports", {
          keyPath: "id",
        });
        reportsStore.createIndex("by-synced", "synced");
        const photosStore = db.createObjectStore("offline-photos", {
          keyPath: "id",
        });
        photosStore.createIndex("by-synced", "synced");
        db.createObjectStore("cached-data", { keyPath: "key" });
      },
    },
  );
}

export async function queueForSync(type: string, data: any) {
  const db = await getOfflineDB();
  await db.add("offline-reports", {
    id: crypto.randomUUID(),
    type,
    data,
    createdAt: new Date().toISOString(),
    synced: false,
  });
  if ("serviceWorker" in navigator && "SyncManager" in window) {
    const registration = await navigator.serviceWorker.ready;
    await registration.sync.register("sync-offline-data");
  }
}
