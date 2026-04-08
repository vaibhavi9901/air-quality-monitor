import AirQualityInfoCard from "../components/widgets/AirQualityInfoCard";
import ProtectionAdviceCard from "../components/widgets/ProtectionAdviceCard";

function Home() {
  return (
    <>
      <div className="grid grid-cols-1 gap-8">
        <AirQualityInfoCard />
        <ProtectionAdviceCard />
      </div>
    </>
  );
}

export default Home;
