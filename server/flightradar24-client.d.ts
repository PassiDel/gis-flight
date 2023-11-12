declare module 'flightradar24-client' {
  function fetchFlight(flight: string): Promise<{
    id: string | null;
    callsign: string | null;
    liveData: boolean;
    model: string | null;
    registration: string | null;
    airline: string | null;
    origin: {
      id: string | null;
      name: string | null;
      coordinates: {
        latitude: number | null;
        longitude: number | null;
        altitude: number | null;
      };
      timezone: string | null;
      country: string | null;
    };
    destination: {
      id: string | null;
      name: string | null;
      coordinates: {
        latitude: number | null;
        longitude: number | null;
        altitude: number | null;
      };
      timezone: string | null;
      country: string | null;
    };
    departure: string | null;
    scheduledDeparture: string | null;
    departureTerminal: string | null;
    departureGate: string | null;
    arrival: string | null;
    scheduledArrival: string | null;
    arrivalTerminal: string | null;
    arrivalGate: string | null;
    delay: number | null;
  }>;

  function fetchFromRadar(
    north: number,
    west: number,
    south: number,
    east: number,
    when?: number,
    opt?: Partial<{
      FAA: boolean;
      FLARM: boolean;
      MLAT: boolean;
      ADSB: boolean;
      inAir: boolean;
      onGround: boolean;
      inactive: boolean;
      gliders: boolean;
      estimatedPositions: boolean;
    }>
  ): Promise<
    {
      id: string;
      registration: string | null;
      flight: string | null;
      callsign: string | null;
      origin: string | null;
      destination: string | null;
      latitude: number;
      longitude: number;
      altitude: number;
      bearing: number;
      speed: number | null;
      rateOfClimb: number;
      isOnGround: boolean;
      squawkCode: string;
      model: string | null;
      modeSCode: string | null;
      radar: string;
      isGlider: boolean;
      timestamp: number | null;
    }[]
  >;
}
