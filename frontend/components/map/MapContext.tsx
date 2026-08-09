'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { apiClient, LayerInfo, MapMetadata } from '@/lib/api';

export type LayerType =
  | 'OSM'
  | 'sentinel_rgb'
  | 'ndvi'
  | 'ndwi'
  | 'ndbi'
  | 'lst'
  | 'ndbi_change'
  | 'lst_change'
  | 'Satellite'
  | 'NDVI'
  | 'NDWI'
  | 'NDBI'
  | 'LST'
  | 'NDBI Change'
  | 'LST Change'
  | string;

export interface LocationGeoBounds {
  center: [number, number]; // [lat, lng]
  zoom: number;
  geojson: any;
}

export interface MapState {
  center: [number, number];
  zoom: number;
  selectedLayer: LayerType;
  opacity: number;
  locationName: string;
  startDate: string;
  endDate: string;
  cloudThreshold: number;
  roiGeoJson: any;
  cursorCoords: { lat: number; lng: number } | null;
  currentZoom: number;
  availableLayers: LayerInfo[];
  tileUrl: string | null;
  metadata: MapMetadata | null;
  isTileLoading: boolean;
  errorMessage: string | null;
}

interface MapContextType {
  state: MapState;
  setSelectedLayer: (layer: LayerType) => void;
  setOpacity: (opacity: number) => void;
  setLocation: (locationName: string) => void;
  setStartDate: (startDate: string) => void;
  setEndDate: (endDate: string) => void;
  setCloudThreshold: (cloudThreshold: number) => void;
  setResearchParameters: (params: {
    location?: string;
    startDate?: string;
    endDate?: string;
    cloudThreshold?: number;
  }) => void;
  setCursorCoords: (coords: { lat: number; lng: number } | null) => void;
  setCurrentZoom: (zoom: number) => void;
  setCenterAndZoom: (center: [number, number], zoom: number) => void;
  refetchTiles: () => Promise<void>;
}

const SAMPLE_HYDERABAD_GEOJSON = {
  type: 'Feature',
  properties: { name: 'Hyderabad Region of Interest' },
  geometry: {
    type: 'Polygon',
    coordinates: [
      [
        [78.35, 17.3],
        [78.6, 17.3],
        [78.6, 17.5],
        [78.35, 17.5],
        [78.35, 17.3],
      ],
    ],
  },
};

const LOCATION_BOUNDS_MAP: Record<string, LocationGeoBounds> = {
  Hyderabad: {
    center: [17.385, 78.4867],
    zoom: 11,
    geojson: SAMPLE_HYDERABAD_GEOJSON,
  },
  Assam: {
    center: [26.2006, 92.9376],
    zoom: 9,
    geojson: {
      type: 'Feature',
      properties: { name: 'Assam Flood Study Region' },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [90.5, 25.8],
            [95.0, 25.8],
            [95.0, 27.5],
            [90.5, 27.5],
            [90.5, 25.8],
          ],
        ],
      },
    },
  },
  'Western Ghats': {
    center: [10.5, 76.5],
    zoom: 8,
    geojson: {
      type: 'Feature',
      properties: { name: 'Western Ghats Canopy Study Region' },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [75.0, 8.5],
            [77.5, 8.5],
            [77.5, 14.0],
            [75.0, 14.0],
            [75.0, 8.5],
          ],
        ],
      },
    },
  },
  Amazon: {
    center: [-3.4653, -62.2159],
    zoom: 7,
    geojson: {
      type: 'Feature',
      properties: { name: 'Amazon Basin Region' },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-70.0, -10.0],
            [-55.0, -10.0],
            [-55.0, 2.0],
            [-70.0, 2.0],
            [-70.0, -10.0],
          ],
        ],
      },
    },
  },
};

const MapContext = createContext<MapContextType | undefined>(undefined);

export function MapProvider({
  children,
  initialLocation = 'Hyderabad',
  initialStartDate = '2016-01-01',
  initialEndDate = '2025-12-31',
  initialCloudThreshold = 20.0,
}: {
  children: ReactNode;
  initialLocation?: string;
  initialStartDate?: string;
  initialEndDate?: string;
  initialCloudThreshold?: number;
}) {
  const locBounds =
    LOCATION_BOUNDS_MAP[initialLocation] ||
    LOCATION_BOUNDS_MAP['Hyderabad'];

  const [state, setState] = useState<MapState>({
    center: locBounds.center,
    zoom: locBounds.zoom,
    selectedLayer: 'OSM',
    opacity: 0.85,
    locationName: initialLocation,
    startDate: initialStartDate,
    endDate: initialEndDate,
    cloudThreshold: initialCloudThreshold,
    roiGeoJson: locBounds.geojson,
    cursorCoords: null,
    currentZoom: locBounds.zoom,
    availableLayers: [],
    tileUrl: null,
    metadata: null,
    isTileLoading: false,
    errorMessage: null,
  });

  // Sync props from parent if initial research parameters change
  useEffect(() => {
    const matched =
      Object.keys(LOCATION_BOUNDS_MAP).find((key) =>
        initialLocation.toLowerCase().includes(key.toLowerCase())
      ) || 'Hyderabad';

    const bounds = LOCATION_BOUNDS_MAP[matched];
    setState((prev) => ({
      ...prev,
      locationName: initialLocation,
      startDate: initialStartDate,
      endDate: initialEndDate,
      cloudThreshold: initialCloudThreshold,
      center: bounds.center,
      zoom: bounds.zoom,
      currentZoom: bounds.zoom,
      roiGeoJson: bounds.geojson,
    }));
  }, [initialLocation, initialStartDate, initialEndDate, initialCloudThreshold]);

  // Fetch available map layers on mount
  useEffect(() => {
    async function loadLayers() {
      try {
        const layers = await apiClient.getMapLayers();
        setState((prev) => ({ ...prev, availableLayers: layers }));
      } catch (err: any) {
        console.warn('Could not load map layers from backend:', err);
      }
    }
    loadLayers();
  }, []);

  const fetchMapTiles = useCallback(
    async (
      location: string,
      startDate: string,
      endDate: string,
      cloudThreshold: number,
      layer: string
    ) => {
      const normalizedLayer =
        layer === 'NDVI'
          ? 'ndvi'
          : layer === 'NDWI'
          ? 'ndwi'
          : layer === 'NDBI'
          ? 'ndbi'
          : layer === 'LST'
          ? 'lst'
          : layer === 'NDBI Change'
          ? 'ndbi_change'
          : layer === 'LST Change'
          ? 'lst_change'
          : layer === 'Satellite'
          ? 'sentinel_rgb'
          : layer;

      setState((prev) => ({ ...prev, isTileLoading: true, errorMessage: null, metadata: null }));
      try {
        const resp = await apiClient.getMapTiles({
          location,
          lat: state.center[0],
          lng: state.center[1],
          zoom: state.zoom,
          start_date: startDate,
          end_date: endDate,
          cloud: cloudThreshold,
          layer: normalizedLayer,
        });

        setState((prev) => ({
          ...prev,
          tileUrl: resp.tile_url,
          metadata: resp.metadata,
          isTileLoading: false,
          errorMessage: null,
        }));
      } catch (err: any) {
        console.error(`Failed to load ${normalizedLayer} map tiles:`, err);
        setState((prev) => ({
          ...prev,
          isTileLoading: false,
          errorMessage: err.message || `Failed to fetch ${normalizedLayer} tiles from Earth Engine backend.`,
        }));
      }
    },
    [state.center, state.zoom]
  );

  // Fetch tiles when layer or research parameters change
  useEffect(() => {
    const layer = state.selectedLayer;
    if (
      layer === 'sentinel_rgb' ||
      layer === 'Satellite' ||
      layer === 'ndvi' ||
      layer === 'NDVI' ||
      layer === 'ndwi' ||
      layer === 'NDWI' ||
      layer === 'ndbi' ||
      layer === 'NDBI' ||
      layer === 'lst' ||
      layer === 'LST' ||
      layer === 'ndbi_change' ||
      layer === 'NDBI Change' ||
      layer === 'lst_change' ||
      layer === 'LST Change'
    ) {
      fetchMapTiles(
        state.locationName,
        state.startDate,
        state.endDate,
        state.cloudThreshold,
        layer
      );
    } else {
      setState((prev) => ({ ...prev, tileUrl: null, errorMessage: null, metadata: null }));
    }
  }, [
    state.selectedLayer,
    state.locationName,
    state.startDate,
    state.endDate,
    state.cloudThreshold,
    fetchMapTiles,
  ]);

  const setSelectedLayer = (selectedLayer: LayerType) => {
    setState((prev) => ({ ...prev, selectedLayer }));
  };

  const setOpacity = (opacity: number) => {
    setState((prev) => ({ ...prev, opacity }));
  };

  const setLocation = (locationName: string) => {
    const matched =
      Object.keys(LOCATION_BOUNDS_MAP).find((key) =>
        locationName.toLowerCase().includes(key.toLowerCase())
      ) || 'Hyderabad';

    const bounds = LOCATION_BOUNDS_MAP[matched];
    setState((prev) => ({
      ...prev,
      locationName,
      center: bounds.center,
      zoom: bounds.zoom,
      currentZoom: bounds.zoom,
      roiGeoJson: bounds.geojson,
    }));
  };

  const setStartDate = (startDate: string) => {
    setState((prev) => ({ ...prev, startDate }));
  };

  const setEndDate = (endDate: string) => {
    setState((prev) => ({ ...prev, endDate }));
  };

  const setCloudThreshold = (cloudThreshold: number) => {
    setState((prev) => ({ ...prev, cloudThreshold }));
  };

  const setResearchParameters = (params: {
    location?: string;
    startDate?: string;
    endDate?: string;
    cloudThreshold?: number;
  }) => {
    setState((prev) => {
      const nextLocation = params.location ?? prev.locationName;
      const matched =
        Object.keys(LOCATION_BOUNDS_MAP).find((key) =>
          nextLocation.toLowerCase().includes(key.toLowerCase())
        ) || 'Hyderabad';

      const bounds = LOCATION_BOUNDS_MAP[matched];
      return {
        ...prev,
        locationName: nextLocation,
        startDate: params.startDate ?? prev.startDate,
        endDate: params.endDate ?? prev.endDate,
        cloudThreshold: params.cloudThreshold ?? prev.cloudThreshold,
        center: bounds.center,
        zoom: bounds.zoom,
        currentZoom: bounds.zoom,
        roiGeoJson: bounds.geojson,
      };
    });
  };

  const setCursorCoords = (cursorCoords: { lat: number; lng: number } | null) => {
    setState((prev) => ({ ...prev, cursorCoords }));
  };

  const setCurrentZoom = (currentZoom: number) => {
    setState((prev) => ({ ...prev, currentZoom }));
  };

  const setCenterAndZoom = (center: [number, number], zoom: number) => {
    setState((prev) => ({ ...prev, center, zoom, currentZoom: zoom }));
  };

  const refetchTiles = async () => {
    const layer = state.selectedLayer;
    if (
      layer === 'sentinel_rgb' ||
      layer === 'Satellite' ||
      layer === 'ndvi' ||
      layer === 'NDVI' ||
      layer === 'ndwi' ||
      layer === 'NDWI' ||
      layer === 'ndbi' ||
      layer === 'NDBI' ||
      layer === 'lst' ||
      layer === 'LST' ||
      layer === 'ndbi_change' ||
      layer === 'NDBI Change' ||
      layer === 'lst_change' ||
      layer === 'LST Change'
    ) {
      await fetchMapTiles(
        state.locationName,
        state.startDate,
        state.endDate,
        state.cloudThreshold,
        layer
      );
    }
  };

  return (
    <MapContext.Provider
      value={{
        state,
        setSelectedLayer,
        setOpacity,
        setLocation,
        setStartDate,
        setEndDate,
        setCloudThreshold,
        setResearchParameters,
        setCursorCoords,
        setCurrentZoom,
        setCenterAndZoom,
        refetchTiles,
      }}
    >
      {children}
    </MapContext.Provider>
  );
}

export function useMapContext() {
  const context = useContext(MapContext);
  if (!context) {
    throw new Error('useMapContext must be used within a MapProvider');
  }
  return context;
}
