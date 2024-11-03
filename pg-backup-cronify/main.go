package main

import (
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

var (
	dbUser       = os.Getenv("PG_USER")
	dbPassword   = os.Getenv("PG_PASSWORD")
	dbName       = os.Getenv("PG_DATABASE")
	dbHost       = os.Getenv("PG_HOST")
	dbPort       = os.Getenv("PG_PORT")
	backupFolder = os.Getenv("BACKUP_FOLDER")
	maxRetries   = 10
	retryDelay   = 2 * time.Second
	cdnHost      = os.Getenv("BUNNY_HOSTNAME")
	cdnStorage   = os.Getenv("BUNNY_STORAGE_NAME")
	cdnAccessKey = os.Getenv("BUNNY_PASSWORD")
)

func main() {
	fmt.Print("\n\n\nLaunching backup at: ", getFormattedDate(), "\n")
	fmt.Println("================================================")

	backupPath, err := pullDBBackup()
	if err != nil {
		fmt.Println("Failed to create db backup:", err)
		os.Exit(1)
	}
	if err := uploadToCDN(backupPath); err != nil {
		fmt.Println("Process failed:", err.Error())
		os.Exit(1)
	}

	fmt.Println("Backup completed successfully. Backup file path:", backupPath)
	os.Exit(1)
}

func pullDBBackup() (string, error) {
	backupFileName := fmt.Sprintf("%s_backup.sql", getFormattedDate())
	backupFolderPath := filepath.Join(getCWD(), "backups", backupFolder)
	backupFilePath := filepath.Join(backupFolderPath, backupFileName)

	if err := os.MkdirAll(backupFolderPath, os.ModePerm); err != nil {
		return "", fmt.Errorf("failed to create backup dir: %w", err)
	}

	for attempt := 1; attempt <= maxRetries; attempt++ {
		fmt.Printf("Attempt %d/%d: Started pulling backup...\n", attempt, maxRetries)

		cmd := exec.Command("pg_dump", "-U", dbUser, "-h", dbHost, "-p", dbPort, "-d", dbName, "-f", backupFilePath)
		cmd.Env = append(os.Environ(), fmt.Sprintf("PGPASSWORD=%s", dbPassword))

		if output, err := cmd.CombinedOutput(); err != nil {
			fmt.Printf("DB backup attempt %d failed: %s\n", attempt, err.Error())
			fmt.Println(string(output))
		} else {
			fmt.Println("DB backup completed successfully:", backupFilePath)
			return backupFilePath, nil
		}

		time.Sleep(retryDelay)
	}
	return "", errors.New("exceeded maximum retry attempts for db backup")
}

func getFormattedDate() string {
	now := time.Now()
	return fmt.Sprintf("%d_%02d_%02d_%02d_%02d_%02d", now.Year(), int(now.Month()), now.Day(), now.Hour(), now.Minute(), now.Second())
}

func getCWD() string {
	dir, _ := os.Getwd()
	return dir
}

func uploadToCDN(backupFilePath string) error {
	for attempt := 1; attempt <= maxRetries; attempt++ {
		fmt.Printf("Attempt %d/%d: Uploading backup to CDN...\n", attempt, maxRetries)

		file, err := os.Open(backupFilePath)
		if err != nil {
			return fmt.Errorf("failed to open backup file: %w", err)
		}
		defer file.Close()

		req, err := http.NewRequest("PUT", fmt.Sprintf("https://%s/%s/%s/%s", cdnHost, cdnStorage, backupFolder, filepath.Base(backupFilePath)), file)
		if err != nil {
			return fmt.Errorf("failed to create request: %w", err)
		}
		req.Header.Set("AccessKey", cdnAccessKey)
		req.Header.Set("Content-Type", "application/octet-stream")

		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			fmt.Printf("CDN upload attempt %d failed: %s\n", attempt, err.Error())
		} else {
			resp.Body.Close()
			if resp.StatusCode == http.StatusCreated {
				fmt.Printf("Backup uploaded successfully on attempt %d.\n", attempt)
				return nil
			} else {
				fmt.Printf("Upload failed with status code %d\n", resp.StatusCode)
			}
		}
		time.Sleep(retryDelay)
	}
	return errors.New("exceeded maximum retry attempts for CDN upload")
}
