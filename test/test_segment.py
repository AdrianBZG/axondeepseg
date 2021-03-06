# coding: utf-8

import pytest
import os
from AxonDeepSeg.segment import *
import AxonDeepSeg.segment

class TestCore(object):
    def setup(self):

        self.testPath = os.path.dirname(os.path.abspath(__file__))

        self.projectPath = os.path.split(self.testPath)[0]

        self.modelPath = os.path.join(
            self.projectPath,
            'AxonDeepSeg',
            'models',
            'default_SEM_model_v1'
            )
        self.imageFolderPath = os.path.join(
            self.testPath,
            '__test_files__',
            '__test_segment_files__'
            )
        self.imagePath = os.path.join(
            self.imageFolderPath,
            'image.png'
            )
        self.imageFolderPathWithPixelSize = os.path.join(
            self.testPath,
            '__test_files__',
            '__test_segment_files_with_pixel_size__'
            )
        self.imagePathWithPixelSize = os.path.join(
            self.imageFolderPathWithPixelSize,
            'image.png'
            )
        self.statsFilename = 'model_statistics_validation.json'

    @classmethod
    def teardown_class(cls):
        testPath = os.path.dirname(os.path.abspath(__file__))
        projectPath = os.path.split(testPath)[0]
        imageFolderPath = os.path.join(
            testPath,
            '__test_files__',
            '__test_segment_files__'
            )

        imageFolderPathWithPixelSize = os.path.join(
            testPath,
            '__test_files__',
            '__test_segment_files_with_pixel_size__'
            )

        outputFiles = [
            'image_seg-axon.png',
            'image_seg-myelin.png',
            'image_seg-axonmyelin.png',
            'image_2_seg-axon.png',
            'image_2_seg-myelin.png',
            'image_2_seg-axonmyelin.png',
            ]

        for fileName in outputFiles:
            if os.path.exists(os.path.join(imageFolderPath, fileName)):
                os.remove(os.path.join(imageFolderPath, fileName))

            if os.path.exists(os.path.join(imageFolderPathWithPixelSize, fileName)):
                os.remove(os.path.join(imageFolderPathWithPixelSize, fileName))

    # --------------generate_config_dict tests-------------- #
    @pytest.mark.unit
    def test_generate_config_dict_outputs_dict(self):

        config = generate_config_dict(
            os.path.join(self.modelPath, 'config_network.json')
            )

        assert type(config) is dict

    @pytest.mark.unit
    def test_generate_config_dict_throws_exception_for_nonexisting_file(self):

        with pytest.raises(ValueError):
            config = generate_config_dict(
                os.path.join(self.modelPath, 'n0n_3xist1ng_f1l3.json')
                )

    # --------------generate_resolution tests-------------- #
    @pytest.mark.unit
    def test_generate_resolution_returns_expected_known_project_cases(self):

        assert generate_resolution('SEM', 512) == 0.1
        assert generate_resolution('SEM', 256) == 0.2
        assert generate_resolution('TEM', 512) == 0.01

    # --------------segment_folders tests-------------- #
    @pytest.mark.integration
    def test_segment_folders_creates_expected_files(self):

        path_model, config = generate_default_parameters('SEM', self.modelPath)

        overlap_value = 25
        resolution_model = generate_resolution('SEM', 512)

        outputFiles = [
            'image_seg-axon.png',
            'image_seg-myelin.png',
            'image_seg-axonmyelin.png'
            ]

        for fileName in outputFiles:
            assert not os.path.exists(
                os.path.join(self.imageFolderPath, fileName)
                )

        segment_folders(
            path_testing_images_folder=self.imageFolderPath,
            path_model=path_model,
            overlap_value=overlap_value,
            config=config,
            resolution_model=resolution_model,
            acquired_resolution=0.37,
            verbosity_level=2
            )

        for fileName in outputFiles:
            assert os.path.exists(os.path.join(self.imageFolderPath, fileName))

    # --------------segment_image tests-------------- #
    @pytest.mark.integration
    def test_segment_image_creates_runs_successfully_(self):
        # Since segment_folders should have already run, the output files
        # should already exist, which this test tests for.

        path_model, config = generate_default_parameters('SEM', self.modelPath)

        overlap_value = 25
        resolution_model = generate_resolution('SEM', 512)

        outputFiles = [
            'image_seg-axon.png',
            'image_seg-myelin.png',
            'image_seg-axonmyelin.png'
            ]

        for fileName in outputFiles:
            assert os.path.exists(os.path.join(self.imageFolderPath, fileName))

        segment_image(
            path_testing_image=self.imagePath,
            path_model=path_model,
            overlap_value=overlap_value,
            config=config,
            resolution_model=resolution_model,
            acquired_resolution=0.37,
            verbosity_level=2
            )

        for fileName in outputFiles:
            assert os.path.exists(os.path.join(self.imageFolderPath, fileName))

    # --------------main (cli) tests-------------- #
    @pytest.mark.integration
    def test_main_cli_runs_succesfully_with_valid_inputs(self):

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imagePath, "-v", "2", "-s", "0.37"])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 0)
   
    @pytest.mark.integration
    def test_main_cli_runs_succesfully_with_valid_inputs_with_pixel_size_file(self):

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imagePathWithPixelSize, "-v", "2"])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 0)

    @pytest.mark.exceptionhandling
    def test_main_cli_handles_exception_for_too_small_resolution_due_to_min_resampled_patch_size(self):

        image_size = [436, 344] # of self.imagePath
        default_SEM_resolution = 0.1
        default_SEM_patch_size = 512

        minimum_resolution = default_SEM_patch_size * default_SEM_resolution / min(image_size)

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imagePath, "-v", "2", "-s", str(round(0.99*minimum_resolution,3))])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 2)

    @pytest.mark.exceptionhandling
    def test_main_cli_handles_exception_missing_resolution_size(self):

        # Make sure that the test folder doesn't have a file named pixel_size_in_micrometer.txt
        assert ~os.path.exists(os.path.join(self.imageFolderPath, 'pixel_size_in_micrometer.txt'))

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imagePath, "-v", "2"])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 3)

    @pytest.mark.integration
    def test_main_cli_runs_succesfully_with_valid_inputs_for_folder_input(self):

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imageFolderPath, "-v", "2", "-s", "0.37"])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 0)

    @pytest.mark.integration
    def test_main_cli_runs_succesfully_with_valid_inputs_for_folder_input_with_pixel_size_file(self):

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imageFolderPathWithPixelSize, "-v", "2"])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 0)

    @pytest.mark.exceptionhandling
    def test_main_cli_handles_exception_for_too_small_resolution_due_to_min_resampled_patch_size_for_folder_input(self):

        image_size = [436, 344] # of self.imagePath
        default_SEM_resolution = 0.1
        default_SEM_patch_size = 512

        minimum_resolution = default_SEM_patch_size * default_SEM_resolution / min(image_size)

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imageFolderPath, "-v", "2", "-s", str(round(0.99*minimum_resolution,3))])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 2)

    @pytest.mark.exceptionhandling
    def test_main_cli_handles_exception_missing_resolution_size_for_folder_input(self):

        # Make sure that the test folder doesn't have a file named pixel_size_in_micrometer.txt
        assert ~os.path.exists(os.path.join(self.imageFolderPath, 'pixel_size_in_micrometer.txt'))

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            AxonDeepSeg.segment.main(["-t", "SEM", "-i", self.imageFolderPath, "-v", "2"])

        assert (pytest_wrapped_e.type == SystemExit) and (pytest_wrapped_e.value.code == 3)