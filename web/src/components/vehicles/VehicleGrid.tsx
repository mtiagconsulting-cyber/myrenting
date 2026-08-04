import VehicleCard from "./VehicleCard";
import type { Vehicle } from "@/types";

export default function VehicleGrid({ vehicles }: { vehicles: Vehicle[] }) {
  return (
    <div className="grid grid-cols-2 gap-3.5 md:grid-cols-4">
      {vehicles.map((v) => (
        <VehicleCard key={v.slug} v={v} />
      ))}
    </div>
  );
}
