// Copyright (C) 2005-2008 Washington University in St Louis, Baylor College of Medicine.  All rights reserved
// Author:        Sasakthi S. Abeysinghe (sasakthi@gmail.com)
// Description:   Performs skeletonization on a grayscale volume

#include "skeletonizer.h"

using namespace wustl_mm::GraySkeletonCPP;

		const char VolumeSkeletonizer::THINNING_CLASS_SURFACE_PRESERVATION = 4;
		const char VolumeSkeletonizer::THINNING_CLASS_CURVE_PRESERVATION_2D = 3;
		const char VolumeSkeletonizer::THINNING_CLASS_CURVE_PRESERVATION = 2;
		const char VolumeSkeletonizer::THINNING_CLASS_POINT_PRESERVATION = 1;
		const char VolumeSkeletonizer::THINNING_CLASS_TOPOLOGY_PRESERVATION = 0;
		const char VolumeSkeletonizer::PRUNING_CLASS_PRUNE_SURFACES = 5;
		const char VolumeSkeletonizer::PRUNING_CLASS_PRUNE_CURVES = 6;
		const char VolumeSkeletonizer::PRUNING_CLASS_PRUNE_POINTS = 7;

		Volume * VolumeSkeletonizer::PerformPureJuSkeletonization(Volume * imageVol, string outputPath, double threshold, int minCurveWidth, int minSurfaceWidth) {
			imageVol->pad(MAX_GAUSSIAN_FILTER_RADIUS, 0);
			Volume * preservedVol = new Volume(imageVol->getSizeX(), imageVol->getSizeY(), imageVol->getSizeZ());
			Volume * surfaceVol;
			Volume * curveVol;
			Volume * topologyVol;
			//printf("\t\t\tUSING THRESHOLD : %f\n", threshold);
			// Skeletonizing while preserving surface features curve features and topology
			surfaceVol = GetJuSurfaceSkeleton(imageVol, preservedVol, threshold);
			PruneSurfaces(surfaceVol, minSurfaceWidth);
			VoxelOr(preservedVol, surfaceVol);
			curveVol = VolumeSkeletonizer::GetJuCurveSkeleton(imageVol, preservedVol, threshold, true);
			VolumeSkeletonizer::PruneCurves(curveVol, minCurveWidth);
			VoxelOr(preservedVol, curveVol);
			topologyVol = VolumeSkeletonizer::GetJuTopologySkeleton(imageVol, preservedVol, threshold);
			imageVol->pad(-MAX_GAUSSIAN_FILTER_RADIUS, 0);
			topologyVol->pad(-MAX_GAUSSIAN_FILTER_RADIUS, 0);
			delete preservedVol;
			delete surfaceVol;
			delete curveVol;
			return topologyVol;
		}

		Volume * VolumeSkeletonizer::GetJuCurveSkeleton(Volume * sourceVolume, Volume * preserve, double threshold, bool is3D){
			char thinningClass = is3D ? THINNING_CLASS_CURVE_PRESERVATION : THINNING_CLASS_CURVE_PRESERVATION_2D;		
			return GetJuThinning(sourceVolume, preserve, threshold, thinningClass);
		}

		Volume * VolumeSkeletonizer::GetJuSurfaceSkeleton(Volume * sourceVolume, Volume * preserve, double threshold){
			return GetJuThinning(sourceVolume, preserve, threshold, THINNING_CLASS_SURFACE_PRESERVATION);
		}

		Volume * VolumeSkeletonizer::GetJuTopologySkeleton(Volume * sourceVolume, Volume * preserve, double threshold){
			return GetJuThinning(sourceVolume, preserve, threshold, THINNING_CLASS_TOPOLOGY_PRESERVATION);
		}

		Volume * VolumeSkeletonizer::GetJuThinning(Volume * sourceVolume, Volume * preserve, double threshold, char thinningClass) {
			Volume * thinnedVolume = new Volume(sourceVolume->getSizeX(), sourceVolume->getSizeY(), sourceVolume->getSizeZ(), 0, 0, 0, sourceVolume);
			switch(thinningClass) {
				case THINNING_CLASS_SURFACE_PRESERVATION :
					thinnedVolume->surfaceSkeletonPres(threshold, preserve);
					break;
				case THINNING_CLASS_CURVE_PRESERVATION :
					thinnedVolume->curveSkeleton(threshold, preserve);
					break;
				case THINNING_CLASS_CURVE_PRESERVATION_2D :
					thinnedVolume->curveSkeleton2D(threshold, preserve);
					break;
				case THINNING_CLASS_TOPOLOGY_PRESERVATION :
					thinnedVolume->skeleton(threshold, preserve, preserve);
			}
			return thinnedVolume;
		}

		void VolumeSkeletonizer::PruneCurves(Volume * sourceVolume, int pruneLength) {
			sourceVolume->erodeHelix(pruneLength);
		}
		void VolumeSkeletonizer::PruneSurfaces(Volume * sourceVolume, int pruneLength) {
			sourceVolume->erodeSheet(pruneLength);
		}

		void VolumeSkeletonizer::VoxelOr(Volume * sourceAndDestVolume1, Volume * sourceVolume2){
			if(sourceVolume2 != NULL) {
				for(int x = 0; x < sourceAndDestVolume1->getSizeX(); x++) {
					for(int y = 0; y < sourceAndDestVolume1->getSizeY(); y++) {
						for(int z = 0; z < sourceAndDestVolume1->getSizeZ(); z++) {
							sourceAndDestVolume1->setDataAt(x, y, z, max(sourceAndDestVolume1->getDataAt(x, y, z), sourceVolume2->getDataAt(x, y, z)));
						}
					}
				}
			}
		}













		//Volume * VolumeSkeletonizer::PerformImmersionSkeletonizationAndPruning(Volume * sourceVol, Volume * preserveVol, double startGray, double endGray, double stepSize, int smoothingIterations, int smoothingRadius, int minCurveSize, int minSurfaceSize, int maxCurveHole, int maxSurfaceHole, string outputPath, bool doPruning, double pointThreshold, double curveThreshold, double surfaceThreshold) {
			//appTimeManager.PushCurrentTime();
			//for(int i = 0; i < smoothingIterations; i++) {
				//SmoothenVolume(sourceVol, startGray, endGray, smoothingRadius);
			//}
			//appTimeManager.PopAndDisplayTime("Smoothing : %f seconds!\n");
			//Vector3DFloat * volumeGradient = NULL;
			//EigenResults3D * volumeEigens;
			//sourceVol->pad(MAX_GAUSSIAN_FILTER_RADIUS, 0);
			//if(preserveVol != NULL) {
				//preserveVol->pad(MAX_GAUSSIAN_FILTER_RADIUS, 0);
			//}

			//if(doPruning) {
				//volumeGradient = GetVolumeGradient(sourceVol);			
			//}

			//Volume * nullVol = new Volume(sourceVol->getSizeX(), sourceVol->getSizeY(), sourceVol->getSizeZ());
			//appTimeManager.PushCurrentTime();
			//Volume * surfaceVol = GetImmersionThinning(sourceVol, preserveVol, startGray, endGray, stepSize, THINNING_CLASS_SURFACE_PRESERVATION);			
			//appTimeManager.PopAndDisplayTime("Surface Thinning : %f seconds!\n");
			
			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//surfaceVol->toMRCFile((char *)(outputPath + "-S-Pre-Prune-Pre-Erode.mrc").c_str());				
			//#endif

			//PruneSurfaces(surfaceVol, minSurfaceSize);

			//appTimeManager.PushCurrentTime();
			//if(doPruning) {
				//#ifdef SAVE_INTERMEDIATE_RESULTS
					//surfaceVol->toMRCFile((char *)(outputPath + "-S-Pre-Prune.mrc").c_str());				
					//WriteVolumeToVRMLFile(surfaceVol, outputPath + "-S-Pre-Prune.wrl");
				//#endif
				//appTimeManager.PushCurrentTime();
				//volumeEigens = GetEigenResults(surfaceVol, volumeGradient, gaussianFilterSurfaceRadius, surfaceRadius, true);
				//appTimeManager.PopAndDisplayTime("  Getting Eigens : %f seconds!\n");

				//appTimeManager.PushCurrentTime();
				//Volume * prunedSurfaceVol = new Volume(surfaceVol->getSizeX(), surfaceVol->getSizeY(), surfaceVol->getSizeZ(), 0, 0, 0, surfaceVol);				
				//appTimeManager.PopAndDisplayTime("  Getting Copy of surface : %f seconds!\n");


				//appTimeManager.PushCurrentTime();
				//PruneUsingStructureTensor(prunedSurfaceVol, sourceVol, preserveVol, volumeGradient, volumeEigens, gaussianFilterSurfaceRadius, surfaceThreshold, PRUNING_CLASS_PRUNE_SURFACES, outputPath + "-S");
				//appTimeManager.PopAndDisplayTime("  Pruning: %f seconds!\n");

				//appTimeManager.PushCurrentTime();
				//delete [] volumeEigens;
				//#ifdef SAVE_INTERMEDIATE_RESULTS
					//prunedSurfaceVol->toMRCFile((char *)(outputPath + "-S-Post-Prune.mrc").c_str());
				//#endif

				//delete surfaceVol;
				//surfaceVol = prunedSurfaceVol;
				//appTimeManager.PopAndDisplayTime("  Memory Cleanup: %f seconds!\n");

			//}		

			//PruneSurfaces(surfaceVol, minSurfaceSize);		
			//appTimeManager.PopAndDisplayTime("Surface Pruning  : %f seconds!\n");

			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//surfaceVol->toMRCFile((char *)(outputPath + "-S-Post-Erosion.mrc").c_str());
			//#endif

			//Volume * cleanedSurfaceVol = GetJuSurfaceSkeleton(surfaceVol, nullVol, 0.5);		
			//PruneSurfaces(cleanedSurfaceVol, minSurfaceSize);
			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//cleanedSurfaceVol->toMRCFile((char *)(outputPath + "-S-Cleaned.mrc").c_str());
			//#endif

			//delete surfaceVol;
			//surfaceVol = cleanedSurfaceVol;
			//VoxelOr(surfaceVol, preserveVol);

			//appTimeManager.PushCurrentTime();

			//Volume * curveVol = GetImmersionThinning(sourceVol, surfaceVol, startGray, endGray, stepSize, THINNING_CLASS_CURVE_PRESERVATION);
			//appTimeManager.PopAndDisplayTime("Curve Thinning   : %f seconds!\n");

			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//curveVol->toMRCFile((char *)(outputPath + "-C-Pre-Prune_Pre-Erode.mrc").c_str());
			//#endif

			//PruneCurves(curveVol, minCurveSize);
			//VoxelBinarySubtract(curveVol, surfaceVol);

			//appTimeManager.PushCurrentTime();
			//if(doPruning) {				
				//#ifdef SAVE_INTERMEDIATE_RESULTS
					//curveVol->toMRCFile((char *)(outputPath + "-C-Pre-Prune.mrc").c_str());
				//#endif

				//volumeEigens = GetEigenResults(curveVol, volumeGradient, gaussianFilterCurveRadius, curveRadius, true);
				//Volume * prunedCurveVol = new Volume(curveVol->getSizeX(), curveVol->getSizeY(), curveVol->getSizeZ(), 0, 0, 0, curveVol);
				//PruneUsingStructureTensor(prunedCurveVol, sourceVol, preserveVol, volumeGradient, volumeEigens, gaussianFilterCurveRadius, curveThreshold, PRUNING_CLASS_PRUNE_CURVES, outputPath + "-C");
				//delete [] volumeEigens;
				//#ifdef SAVE_INTERMEDIATE_RESULTS
					//prunedCurveVol->toMRCFile((char *)(outputPath + "-C-Post-Prune.mrc").c_str());
				//#endif

				//Volume * filledCurveVol = FillCurveHoles(prunedCurveVol, curveVol, maxCurveHole);
				//#ifdef SAVE_INTERMEDIATE_RESULTS
					//filledCurveVol->toMRCFile((char *)(outputPath + "-C-Post-Fill.mrc").c_str());
				//#endif
				//delete curveVol;
				//delete prunedCurveVol;
				//curveVol = filledCurveVol;

				
			//}

			//VoxelOr(curveVol, surfaceVol);
			//PruneCurves(curveVol, minCurveSize);		
			//appTimeManager.PopAndDisplayTime("Curve Pruning    : %f seconds!\n");
			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//curveVol->toMRCFile((char *)(outputPath + "-C-Post-Erosion.mrc").c_str());
			//#endif

			//Volume * cleanedCurveVol = GetJuCurveSkeleton(curveVol, surfaceVol, 0.5, true);		
			//PruneCurves(cleanedCurveVol, minCurveSize);		
			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//cleanedCurveVol->toMRCFile((char *)(outputPath + "-C-Cleaned.mrc").c_str());
			//#endif

			//delete curveVol;
			//curveVol = cleanedCurveVol;

			//VoxelOr(curveVol, surfaceVol);
			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//curveVol->toMRCFile((char *)(outputPath + "-SC.mrc").c_str());
			//#endif
			
			//// Removed as points will never be preserved.
			//// Volume * pointVol = GetImmersionThinning(sourceVol, curveVol, startGray, endGray, stepSize, THINNING_CLASS_POINT_PRESERVATION);
			////if(doPruning) {
			////	pointVol->toMRCFile((char *)(outputPath + "-P-Pre-Prune.mrc").c_str());
			////	volumeEigens = GetEigenResults2(pointVol, volumeGradient, gaussianFilterPointRadius, pointRadius, true);
			////	PruneUsingStructureTensor(pointVol, sourceVol, volumeEigens, pointThreshold, PRUNING_CLASS_PRUNE_POINTS, outputPath + "-P");
			////	delete [] volumeEigens;
			////	pointVol->toMRCFile((char *)(outputPath + "-P-Post-Prune.mrc").c_str());
			////}

			////VoxelOr(pointVol, curveVol);

			//delete surfaceVol;
			////delete curveVol;
			//delete nullVol;
			//delete [] volumeGradient;

			//#ifdef SAVE_INTERMEDIATE_RESULTS
				//curveVol->toOFFCells2((char *)(outputPath + "-SC.off").c_str());
			//#endif

			//sourceVol->pad(-MAX_GAUSSIAN_FILTER_RADIUS, 0);
			//curveVol->pad(-MAX_GAUSSIAN_FILTER_RADIUS, 0);			
			//return curveVol;					
		//}
