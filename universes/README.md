# BusinessObjects Universe Files

This directory contains BusinessObjects universe files (.unv and .unx) for migration to SAC/Datasphere.

## Files

### UNX Files (BusinessObjects 4.x XML format)
- **LIG_Blank_Inventory.unx** (13 KB) - Blank inventory universe
- **SOM_BL.unx** (18 KB) - SOM business layer
- **SeasonDemo_BL.unx** (17 KB) - Season demo business layer

### UNV Files (BusinessObjects 3.x binary format)
- **RW_InventoryAnalysis_NetAvailable.unv** (560 KB) - Inventory analysis with net available metrics
- **RW_InventoryAnalysis_Weekly_Buckets_Seperate.unv** (730 KB) - Inventory analysis with weekly buckets (separate)
- **RW_MasterData.unv** (472 KB) - Master data universe
- **RW_PLM.unv** (414 KB) - PLM (Product Lifecycle Management) universe
- **RW_SalesAndOperations.unv** (961 KB) - Sales and operations universe

## Usage

To convert a universe file:

```bash
cd /Users/I870089/migration_studio/backend
python -m app.engines.bobj2sac.cli convert <universe_file> --out <output_directory>
```

Example:
```bash
python -m app.engines.bobj2sac.cli convert ../universes/RW_SalesAndOperations.unv --out ../output
```

## File Information

- **Added:** March 5, 2026
- **Source:** Downloaded from SAP BusinessObjects system
- **Total Files:** 8 (3 UNX + 5 UNV)
- **Total Size:** ~3.2 MB
