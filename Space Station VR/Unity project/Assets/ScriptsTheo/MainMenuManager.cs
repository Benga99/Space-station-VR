using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using Valve.VR.Extras;
using UnityEngine.UI;

public class MainMenuManager : MonoBehaviour
{
    [Header("Lasers")]
    public SteamVR_LaserPointer laserPointerRight;
    public SteamVR_LaserPointer laserPointerLeft;

    [Header("Panels")]
    public GameObject StartPanel;
    public GameObject ChooseRoomsPanel;
    public GameObject HowToPlayPanel;

    [Header("Buttons")]
    public GameObject startButton;
    public GameObject howToPlayButton;
    public GameObject settingsButton;
    public GameObject exitButton;

    public GameObject room1Button;
    public GameObject room2Button;
    public GameObject room3Button;
    public GameObject room4Button;
    public GameObject backToStartButton;
    public GameObject backfromHTPToStartButton;

    [Header("Player")]
    public GameObject player;


    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void ExitGame()
    {
        Application.Quit();
    }

    

    void Awake()
    {
        laserPointerRight.PointerIn += PointerInside;
        laserPointerRight.PointerOut += PointerOutside;
        laserPointerRight.PointerClick += PointerClick;

        laserPointerLeft.PointerIn += PointerInside;
        laserPointerLeft.PointerOut += PointerOutside;
        laserPointerLeft.PointerClick += PointerClick;
    }

    public void PointerClick(object sender, PointerEventArgs e)
    {
        //if (!e.target.CompareTag("UI")) { return; }
        switch (e.target.name)
        {
            case "StartButton":
                ChooseRoomsPanel.SetActive(true);
                StartPanel.SetActive(false);
                break;

            case "HowToPlayButton":
                HowToPlayPanel.SetActive(true);
                StartPanel.SetActive(false);
                startButton.GetComponent<Button>().interactable = true;
                startButton.GetComponent<BoxCollider>().size = new Vector3(400, 140, 50);
                break;

            case "SettingsButton":

                break;

            case "ExitButton":
                ExitGame();
                break;

            case "Room1Button":
                LoadScene(1);
                break;

            case "Room2Button":
                LoadScene(2);
                break;

            case "Room3Button":
                LoadScene(3);
                break;

            case "Room4Button":
                LoadScene(4);
                break;

            case "BackToStartButton":
                ChooseRoomsPanel.SetActive(false);
                StartPanel.SetActive(true);
                break;

            case "BackFromHTPToStartButton":
                HowToPlayPanel.SetActive(false);
                StartPanel.SetActive(true);
                break;
                


            default:
                break;

        }
    }

    private void LoadScene(int buildIndex)
    {
        Destroy(player);
        SceneManager.LoadScene(buildIndex);
    }

    public void PointerInside(object sender, PointerEventArgs e)
    {
        //if (!e.target.("UI")) { return; }
        switch (e.target.name)
        {
            case "StartButton":
                if(startButton.GetComponent<Button>().interactable == true)
                {
                    startButton.GetComponent<Image>().color = Color.green;  
                }
                break;

            case "HowToPlayButton":
                howToPlayButton.GetComponent<Image>().color = Color.green;
                break;

            case "SettingsButton":
                settingsButton.GetComponent<Image>().color = Color.green;
                break;

            case "ExitButton":
                exitButton.GetComponent<Image>().color = Color.green;
                break;

            case "Room1Button":
                room1Button.GetComponent<Image>().color = Color.green;
                break;

            case "Room2Button":
                room2Button.GetComponent<Image>().color = Color.green;
                break;

            case "Room3Button":
                room3Button.GetComponent<Image>().color = Color.green;
                break;

            case "Room4Button":
                room4Button.GetComponent<Image>().color = Color.green;
                break;

            case "BackToStartButton":
                backToStartButton.GetComponent<Image>().color = Color.green;
                break;

            case "BackFromHTPToStartButton":
                backfromHTPToStartButton.GetComponent<Image>().color = Color.green;
                break;



            default:
                break;

        }
    }

    public void PointerOutside(object sender, PointerEventArgs e)
    {
        //if (!e.target.CompareTag("UI")) { return; }
        switch (e.target.name)
        {
            case "StartButton":
                if (startButton.GetComponent<Button>().interactable == true)
                {
                    startButton.GetComponent<Image>().color = Color.white;
                }
                break;

            case "HowToPlayButton":
                howToPlayButton.GetComponent<Image>().color = Color.white;
                break;

            case "SettingsButton":
                settingsButton.GetComponent<Image>().color = Color.white;
                break;

            case "ExitButton":
                exitButton.GetComponent<Image>().color = Color.white;
                break;

            case "Room1Button":
                room1Button.GetComponent<Image>().color = Color.white;
                break;

            case "Room2Button":
                room2Button.GetComponent<Image>().color = Color.white;
                break;

            case "Room3Button":
                room3Button.GetComponent<Image>().color = Color.white;
                break;

            case "Room4Button":
                room4Button.GetComponent<Image>().color = Color.white;
                break;

            case "BackToStartButton":
                backToStartButton.GetComponent<Image>().color = Color.white;
                break;

            case "BackFromHTPToStartButton":
                backfromHTPToStartButton.GetComponent<Image>().color = Color.white;
                break;



            default:
                break;

        }
    }
}
